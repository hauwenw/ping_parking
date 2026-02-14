"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiError } from "@/lib/api";
import type { Customer } from "@/lib/types";
import { formatPhone } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
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
import Link from "next/link";

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Customer | null>(null);
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    const data = await api.get<Customer[]>(`/api/v1/customers?${params.toString()}`);
    setCustomers(data);
    setLoading(false);
  }, [search]);

  useEffect(() => { load(); }, [load]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const body = {
      name: form.get("name") as string,
      phone: form.get("phone") as string,
      contact_phone: (form.get("contact_phone") as string) || null,
      email: (form.get("email") as string) || null,
      notes: (form.get("notes") as string) || null,
    };
    try {
      if (editing) {
        await api.put(`/api/v1/customers/${editing.id}`, body);
        toast.success("客戶已更新");
      } else {
        await api.post("/api/v1/customers", body);
        toast.success("客戶已新增");
      }
      setDialogOpen(false);
      setEditing(null);
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  const handleDelete = async (c: Customer) => {
    if (!confirm(`確定要刪除「${c.name}」嗎？`)) return;
    try {
      await api.delete(`/api/v1/customers/${c.id}`);
      toast.success("客戶已刪除");
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">客戶管理</h2>
        <Dialog open={dialogOpen} onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) setEditing(null);
        }}>
          <DialogTrigger asChild>
            <Button>新增客戶</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editing ? "編輯客戶" : "新增客戶"}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">姓名</Label>
                  <Input id="name" name="name" defaultValue={editing?.name} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">手機號碼</Label>
                  <Input id="phone" name="phone" placeholder="09XXXXXXXX" defaultValue={editing?.phone} required />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="contact_phone">聯絡電話</Label>
                  <Input id="contact_phone" name="contact_phone" defaultValue={editing?.contact_phone || ""} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">電子郵件</Label>
                  <Input id="email" name="email" type="email" defaultValue={editing?.email || ""} />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="notes">備註</Label>
                <Input id="notes" name="notes" defaultValue={editing?.notes || ""} />
              </div>
              <Button type="submit" className="w-full">{editing ? "儲存" : "新增"}</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search bar */}
      <div className="flex items-center gap-2">
        <Input
          placeholder="搜尋姓名或電話..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
      </div>

      {loading ? (
        <p className="text-muted-foreground">載入中...</p>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>姓名</TableHead>
                <TableHead>手機</TableHead>
                <TableHead>聯絡電話</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>有效合約</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {customers.map((c) => (
                <TableRow key={c.id}>
                  <TableCell>
                    <Link
                      href={`/customers/${c.id}`}
                      className="font-medium text-primary hover:underline"
                    >
                      {c.name}
                    </Link>
                  </TableCell>
                  <TableCell>{formatPhone(c.phone)}</TableCell>
                  <TableCell>{c.contact_phone ? formatPhone(c.contact_phone) : "-"}</TableCell>
                  <TableCell>{c.email || "-"}</TableCell>
                  <TableCell>
                    {c.active_agreement_count > 0 ? (
                      <Link href={`/agreements?customer_id=${c.id}`}>
                        <Badge className="cursor-pointer">{c.active_agreement_count}</Badge>
                      </Link>
                    ) : (
                      <span className="text-muted-foreground">0</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="outline" size="sm" onClick={() => {
                      setEditing(c);
                      setDialogOpen(true);
                    }}>編輯</Button>
                    <Button variant="destructive" size="sm" onClick={() => handleDelete(c)}>刪除</Button>
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
