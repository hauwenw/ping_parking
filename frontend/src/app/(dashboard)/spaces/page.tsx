"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { api, ApiError } from "@/lib/api";
import type { Space, Site, Tag } from "@/lib/types";
import { spaceStatusLabel, formatCurrency } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";

const statusColor: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  available: "default",
  occupied: "secondary",
  reserved: "outline",
  maintenance: "destructive",
};

const priceTierLabel: Record<string, string> = {
  site: "場地",
  tag: "標籤",
  custom: "自訂",
};

function generatePreviewNames(prefix: string, start: number, count: number): string[] {
  const maxNum = start + count - 1;
  const pad = maxNum > 99 ? 3 : 2;
  return Array.from({ length: count }, (_, i) =>
    `${prefix}-${String(start + i).padStart(pad, "0")}`
  );
}

export default function SpacesPage() {
  const [spaces, setSpaces] = useState<Space[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [batchDialogOpen, setBatchDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Space | null>(null);
  const [filterSite, setFilterSite] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterTag, setFilterTag] = useState<string>("all");

  // Batch create form state
  const [batchSiteId, setBatchSiteId] = useState<string>("");
  const [batchPrefix, setBatchPrefix] = useState<string>("");
  const [batchStart, setBatchStart] = useState<number>(1);
  const [batchCount, setBatchCount] = useState<number>(10);

  // Edit form state
  const [editName, setEditName] = useState("");
  const [editStatus, setEditStatus] = useState("available");
  const [editTags, setEditTags] = useState<string[]>([]);
  const [editCustomPrice, setEditCustomPrice] = useState<string>("");

  const load = useCallback(async () => {
    const params = new URLSearchParams();
    if (filterSite !== "all") params.set("site_id", filterSite);
    if (filterStatus !== "all") params.set("status", filterStatus);
    if (filterTag !== "all") params.set("tag", filterTag);

    const [spacesData, sitesData, tagsData] = await Promise.all([
      api.get<Space[]>(`/api/v1/spaces?${params.toString()}`),
      api.get<Site[]>("/api/v1/sites"),
      api.get<Tag[]>("/api/v1/tags"),
    ]);
    setSpaces(spacesData);
    setSites(sitesData);
    setTags(tagsData);
    setLoading(false);
  }, [filterSite, filterStatus, filterTag]);

  useEffect(() => { load(); }, [load]);

  const openEditDialog = (space: Space) => {
    setEditing(space);
    setEditName(space.name);
    setEditStatus(space.status);
    setEditTags([...space.tags]);
    setEditCustomPrice(space.custom_price != null ? String(space.custom_price) : "");
    setEditDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const body = {
      site_id: form.get("site_id") as string,
      name: form.get("name") as string,
    };
    try {
      await api.post("/api/v1/spaces", body);
      toast.success("車位已新增");
      setDialogOpen(false);
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  const handleBatchSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await api.post("/api/v1/spaces/batch", {
        site_id: batchSiteId,
        prefix: batchPrefix,
        start: batchStart,
        count: batchCount,
      });
      toast.success(`已新增 ${batchCount} 個車位`);
      setBatchDialogOpen(false);
      setBatchPrefix("");
      setBatchStart(1);
      setBatchCount(10);
      setBatchSiteId("");
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  const handleEditSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!editing) return;
    const body: Record<string, unknown> = {
      name: editName,
      status: editStatus,
      tags: editTags,
    };
    if (editCustomPrice !== "") {
      body.custom_price = Number(editCustomPrice);
    } else {
      body.custom_price = null;
    }
    try {
      await api.put(`/api/v1/spaces/${editing.id}`, body);
      toast.success("車位已更新");
      setEditDialogOpen(false);
      setEditing(null);
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  const handleDelete = async (space: Space) => {
    if (!confirm(`確定要刪除車位「${space.name}」嗎？`)) return;
    try {
      await api.delete(`/api/v1/spaces/${space.id}`);
      toast.success("車位已刪除");
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  const toggleTag = (tagName: string) => {
    setEditTags((prev) =>
      prev.includes(tagName)
        ? prev.filter((t) => t !== tagName)
        : [...prev, tagName]
    );
  };

  const tagColorMap = useMemo(() => {
    const map: Record<string, string> = {};
    for (const t of tags) map[t.name] = t.color;
    return map;
  }, [tags]);

  const previewNames = useMemo(() => {
    if (!batchPrefix || batchCount < 1 || batchStart < 1) return [];
    return generatePreviewNames(batchPrefix, batchStart, batchCount);
  }, [batchPrefix, batchStart, batchCount]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">車位管理</h2>
        <div className="flex gap-2">
          <Dialog open={batchDialogOpen} onOpenChange={setBatchDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">批次新增</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>批次新增車位</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleBatchSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label>停車場</Label>
                  <Select value={batchSiteId} onValueChange={setBatchSiteId} required>
                    <SelectTrigger>
                      <SelectValue placeholder="選擇停車場" />
                    </SelectTrigger>
                    <SelectContent>
                      {sites.map((s) => (
                        <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="batch-prefix">前綴</Label>
                  <Input
                    id="batch-prefix"
                    value={batchPrefix}
                    onChange={(e) => setBatchPrefix(e.target.value)}
                    placeholder="A"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="batch-start">起始編號</Label>
                    <Input
                      id="batch-start"
                      type="number"
                      min={1}
                      max={999}
                      value={batchStart}
                      onChange={(e) => setBatchStart(Number(e.target.value))}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="batch-count">數量</Label>
                    <Input
                      id="batch-count"
                      type="number"
                      min={1}
                      max={100}
                      value={batchCount}
                      onChange={(e) => setBatchCount(Number(e.target.value))}
                      required
                    />
                  </div>
                </div>
                {previewNames.length > 0 && (
                  <div className="rounded-md bg-muted p-3">
                    <p className="text-sm text-muted-foreground mb-1">
                      將建立 {previewNames.length} 個車位：
                    </p>
                    <p className="text-sm font-mono">
                      {previewNames.length <= 8
                        ? previewNames.join(", ")
                        : `${previewNames.slice(0, 4).join(", ")}, ... , ${previewNames.slice(-2).join(", ")}`}
                    </p>
                  </div>
                )}
                <Button type="submit" className="w-full" disabled={!batchSiteId || !batchPrefix}>
                  批次新增
                </Button>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>新增車位</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>新增車位</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label>停車場</Label>
                  <Select name="site_id" required>
                    <SelectTrigger>
                      <SelectValue placeholder="選擇停車場" />
                    </SelectTrigger>
                    <SelectContent>
                      {sites.map((s) => (
                        <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="name">車位名稱</Label>
                  <Input id="name" name="name" placeholder="A-01" required />
                </div>
                <Button type="submit" className="w-full">新增</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={(open) => {
        setEditDialogOpen(open);
        if (!open) setEditing(null);
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>編輯車位</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEditSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">車位名稱</Label>
              <Input
                id="edit-name"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label>狀態</Label>
              <Select value={editStatus} onValueChange={setEditStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="available">可用</SelectItem>
                  <SelectItem value="occupied">已占用</SelectItem>
                  <SelectItem value="reserved">已預約</SelectItem>
                  <SelectItem value="maintenance">維護中</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>標籤</Label>
              <div className="rounded-md border p-3 space-y-2 max-h-48 overflow-y-auto">
                {tags.length === 0 ? (
                  <p className="text-sm text-muted-foreground">尚無標籤</p>
                ) : (
                  tags.map((t) => (
                    <label key={t.id} className="flex items-center gap-2 cursor-pointer">
                      <Checkbox
                        checked={editTags.includes(t.name)}
                        onCheckedChange={() => toggleTag(t.name)}
                      />
                      <span
                        className="inline-block h-3 w-3 rounded-full shrink-0"
                        style={{ backgroundColor: t.color || "#6B7280" }}
                      />
                      <span className="text-sm">{t.name}</span>
                    </label>
                  ))
                )}
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-custom-price">自訂月租價格</Label>
              <Input
                id="edit-custom-price"
                type="number"
                min={0}
                value={editCustomPrice}
                onChange={(e) => setEditCustomPrice(e.target.value)}
                placeholder="留空則使用標籤或場地價格"
              />
              <p className="text-xs text-muted-foreground">
                設定後將覆蓋標籤和場地價格。清空則恢復預設。
              </p>
            </div>
            <Button type="submit" className="w-full">儲存</Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        <Select value={filterSite} onValueChange={setFilterSite}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="停車場" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部停車場</SelectItem>
            {sites.map((s) => (
              <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="狀態" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部狀態</SelectItem>
            <SelectItem value="available">可用</SelectItem>
            <SelectItem value="occupied">已占用</SelectItem>
            <SelectItem value="reserved">已預約</SelectItem>
            <SelectItem value="maintenance">維護中</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filterTag} onValueChange={setFilterTag}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="標籤" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部標籤</SelectItem>
            {tags.map((t) => (
              <SelectItem key={t.id} value={t.name}>
                <span className="flex items-center gap-1.5">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: t.color || "#6B7280" }}
                  />
                  {t.name}
                </span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <p className="text-muted-foreground">載入中...</p>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>車位</TableHead>
                <TableHead>停車場</TableHead>
                <TableHead>狀態</TableHead>
                <TableHead>標籤</TableHead>
                <TableHead>月租價格</TableHead>
                <TableHead>價格來源</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {spaces.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-medium">{s.name}</TableCell>
                  <TableCell>{s.site_name}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Badge variant={statusColor[s.computed_status || s.status] || "default"}>
                        {spaceStatusLabel(s.computed_status || s.status)}
                      </Badge>
                      {s.active_agreement_id && (
                        <a
                          href={`/agreements/${s.active_agreement_id}`}
                          className="text-xs text-blue-600 hover:underline"
                        >
                          查看合約
                        </a>
                      )}
                      <a
                        href={`/agreements?create=true&space_id=${s.id}`}
                        className="text-xs text-green-600 hover:underline"
                      >
                        新增合約
                      </a>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      {s.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="flex items-center gap-1">
                          <span
                            className="inline-block h-2.5 w-2.5 rounded-full shrink-0"
                            style={{ backgroundColor: tagColorMap[tag] || "#6B7280" }}
                          />
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    {s.effective_monthly_price != null
                      ? formatCurrency(s.effective_monthly_price)
                      : "-"}
                  </TableCell>
                  <TableCell>
                    {s.price_tier ? (
                      <Badge variant="secondary">
                        {priceTierLabel[s.price_tier] || s.price_tier}
                        {s.price_tag_name ? `(${s.price_tag_name})` : ""}
                      </Badge>
                    ) : "-"}
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="outline" size="sm" onClick={() => openEditDialog(s)}>
                      編輯
                    </Button>
                    <Button variant="destructive" size="sm" onClick={() => handleDelete(s)}>
                      刪除
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
