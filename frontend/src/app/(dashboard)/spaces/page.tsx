"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiError } from "@/lib/api";
import type { Space, Site } from "@/lib/types";
import { spaceStatusLabel } from "@/lib/format";
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

export default function SpacesPage() {
  const [spaces, setSpaces] = useState<Space[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [filterSite, setFilterSite] = useState<string>("all");

  const load = useCallback(async () => {
    const [spacesData, sitesData] = await Promise.all([
      api.get<Space[]>("/api/v1/spaces"),
      api.get<Site[]>("/api/v1/sites"),
    ]);
    setSpaces(spacesData);
    setSites(sitesData);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const filteredSpaces = filterSite === "all"
    ? spaces
    : spaces.filter((s) => s.site_id === filterSite);

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
        <div className="flex items-center gap-2">
          <Select value={filterSite} onValueChange={setFilterSite}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="篩選停車場" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部</SelectItem>
              {sites.map((s) => (
                <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
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
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSpaces.map((s) => (
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
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
