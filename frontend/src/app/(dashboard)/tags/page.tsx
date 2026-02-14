"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiError } from "@/lib/api";
import type { Tag } from "@/lib/types";
import { formatCurrency } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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

export default function TagsPage() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Tag | null>(null);

  const load = useCallback(async () => {
    const data = await api.get<Tag[]>("/api/v1/tags");
    setTags(data);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const body = {
      name: form.get("name") as string,
      color: form.get("color") as string,
      description: (form.get("description") as string) || null,
      monthly_price: form.get("monthly_price") ? Number(form.get("monthly_price")) : null,
      daily_price: form.get("daily_price") ? Number(form.get("daily_price")) : null,
    };
    try {
      if (editing) {
        await api.put(`/api/v1/tags/${editing.id}`, body);
        toast.success("標籤已更新");
      } else {
        await api.post("/api/v1/tags", body);
        toast.success("標籤已新增");
      }
      setDialogOpen(false);
      setEditing(null);
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  const handleDelete = async (tag: Tag) => {
    if (!confirm(`確定要刪除「${tag.name}」嗎？`)) return;
    try {
      await api.delete(`/api/v1/tags/${tag.id}`);
      toast.success("標籤已刪除");
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">標籤管理</h2>
        <Dialog open={dialogOpen} onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) setEditing(null);
        }}>
          <DialogTrigger asChild>
            <Button>新增標籤</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editing ? "編輯標籤" : "新增標籤"}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">名稱</Label>
                  <Input id="name" name="name" defaultValue={editing?.name} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="color">顏色</Label>
                  <Input id="color" name="color" type="color" defaultValue={editing?.color || "#3B82F6"} required />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">說明</Label>
                <Input id="description" name="description" defaultValue={editing?.description || ""} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="monthly_price">月租價格</Label>
                  <Input id="monthly_price" name="monthly_price" type="number" min="0" defaultValue={editing?.monthly_price || ""} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="daily_price">日租價格</Label>
                  <Input id="daily_price" name="daily_price" type="number" min="0" defaultValue={editing?.daily_price || ""} />
                </div>
              </div>
              <Button type="submit" className="w-full">{editing ? "儲存" : "新增"}</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <p className="text-muted-foreground">載入中...</p>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>顏色</TableHead>
                <TableHead>名稱</TableHead>
                <TableHead>說明</TableHead>
                <TableHead>月租價格</TableHead>
                <TableHead>日租價格</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tags.map((tag) => (
                <TableRow key={tag.id}>
                  <TableCell>
                    <div className="h-5 w-5 rounded-full" style={{ backgroundColor: tag.color }} />
                  </TableCell>
                  <TableCell className="font-medium">{tag.name}</TableCell>
                  <TableCell>{tag.description || "-"}</TableCell>
                  <TableCell>{tag.monthly_price != null ? formatCurrency(tag.monthly_price) : "-"}</TableCell>
                  <TableCell>{tag.daily_price != null ? formatCurrency(tag.daily_price) : "-"}</TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="outline" size="sm" onClick={() => {
                      setEditing(tag);
                      setDialogOpen(true);
                    }}>編輯</Button>
                    <Button variant="destructive" size="sm" onClick={() => handleDelete(tag)}>刪除</Button>
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
