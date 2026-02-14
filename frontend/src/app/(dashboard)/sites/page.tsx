"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiError } from "@/lib/api";
import type { Site } from "@/lib/types";
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

export default function SitesPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingSite, setEditingSite] = useState<Site | null>(null);

  const loadSites = useCallback(async () => {
    const data = await api.get<Site[]>("/api/v1/sites");
    setSites(data);
    setLoading(false);
  }, []);

  useEffect(() => { loadSites(); }, [loadSites]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const body = {
      name: form.get("name") as string,
      address: (form.get("address") as string) || null,
      monthly_base_price: Number(form.get("monthly_base_price")),
      daily_base_price: Number(form.get("daily_base_price")),
    };
    try {
      if (editingSite) {
        await api.put(`/api/v1/sites/${editingSite.id}`, body);
        toast.success("停車場已更新");
      } else {
        await api.post("/api/v1/sites", body);
        toast.success("停車場已新增");
      }
      setDialogOpen(false);
      setEditingSite(null);
      await loadSites();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  const handleDelete = async (site: Site) => {
    if (!confirm(`確定要刪除「${site.name}」嗎？`)) return;
    try {
      await api.delete(`/api/v1/sites/${site.id}`);
      toast.success("停車場已刪除");
      await loadSites();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">停車場管理</h2>
        <Dialog open={dialogOpen} onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) setEditingSite(null);
        }}>
          <DialogTrigger asChild>
            <Button>新增停車場</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingSite ? "編輯停車場" : "新增停車場"}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">名稱</Label>
                <Input id="name" name="name" defaultValue={editingSite?.name} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="address">地址</Label>
                <Input id="address" name="address" defaultValue={editingSite?.address || ""} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="monthly_base_price">月租基本價</Label>
                  <Input id="monthly_base_price" name="monthly_base_price" type="number" min="0" defaultValue={editingSite?.monthly_base_price || 0} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="daily_base_price">日租基本價</Label>
                  <Input id="daily_base_price" name="daily_base_price" type="number" min="0" defaultValue={editingSite?.daily_base_price || 0} required />
                </div>
              </div>
              <Button type="submit" className="w-full">{editingSite ? "儲存" : "新增"}</Button>
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
                <TableHead>名稱</TableHead>
                <TableHead>地址</TableHead>
                <TableHead>月租基本價</TableHead>
                <TableHead>日租基本價</TableHead>
                <TableHead>車位數</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sites.map((site) => (
                <TableRow key={site.id}>
                  <TableCell className="font-medium">{site.name}</TableCell>
                  <TableCell>{site.address || "-"}</TableCell>
                  <TableCell>{formatCurrency(site.monthly_base_price)}</TableCell>
                  <TableCell>{formatCurrency(site.daily_base_price)}</TableCell>
                  <TableCell>{site.space_count}</TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="outline" size="sm" onClick={() => {
                      setEditingSite(site);
                      setDialogOpen(true);
                    }}>編輯</Button>
                    <Button variant="destructive" size="sm" onClick={() => handleDelete(site)}>刪除</Button>
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
