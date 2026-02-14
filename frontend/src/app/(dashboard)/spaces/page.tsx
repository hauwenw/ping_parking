"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiError } from "@/lib/api";
import type { Space, Site, Tag } from "@/lib/types";
import { spaceStatusLabel, formatCurrency } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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

export default function SpacesPage() {
  const [spaces, setSpaces] = useState<Space[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [filterSite, setFilterSite] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterTag, setFilterTag] = useState<string>("all");

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

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">車位管理</h2>
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
              <SelectItem key={t.id} value={t.name}>{t.name}</SelectItem>
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
              </TableRow>
            </TableHeader>
            <TableBody>
              {spaces.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-medium">{s.name}</TableCell>
                  <TableCell>{s.site_name}</TableCell>
                  <TableCell>
                    <Badge variant={statusColor[s.status] || "default"}>
                      {spaceStatusLabel(s.status)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      {s.tags.map((tag) => (
                        <Badge key={tag} variant="outline">{tag}</Badge>
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
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
