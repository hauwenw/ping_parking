"use client";

import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import type { Agreement, AgreementSummary, Customer, Space } from "@/lib/types";
import { formatCurrency, formatDate, agreementTypeLabel, paymentStatusLabel } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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

export default function AgreementsPage() {
  const searchParams = useSearchParams();
  const customerIdParam = searchParams.get("customer_id");

  const [agreements, setAgreements] = useState<Agreement[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [spaces, setSpaces] = useState<Space[]>([]);
  const [summary, setSummary] = useState<AgreementSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [terminateId, setTerminateId] = useState<string | null>(null);

  // Price auto-population state
  const [selectedSpaceId, setSelectedSpaceId] = useState<string | null>(null);
  const [selectedAgreementType, setSelectedAgreementType] = useState<string | null>(null);
  const [priceValue, setPriceValue] = useState<string>("");

  // Pre-selected space from URL (for quick create from spaces page)
  const [preselectedSpaceId, setPreselectedSpaceId] = useState<string | null>(null);

  const load = useCallback(async () => {
    const params = new URLSearchParams();
    if (customerIdParam) params.set("customer_id", customerIdParam);

    const [agreementsData, customersData, spacesData, summaryData] = await Promise.all([
      api.get<Agreement[]>(`/api/v1/agreements?${params.toString()}`),
      api.get<Customer[]>("/api/v1/customers"),
      api.get<Space[]>("/api/v1/spaces"),
      api.get<AgreementSummary>("/api/v1/agreements/summary"),
    ]);
    setAgreements(agreementsData);
    setCustomers(customersData);
    setSpaces(spacesData);
    setSummary(summaryData);
    setLoading(false);
  }, [customerIdParam]);

  useEffect(() => { load(); }, [load]);

  // Handle URL params for quick agreement creation from spaces page
  useEffect(() => {
    const shouldCreate = searchParams.get("create") === "true";
    const spaceId = searchParams.get("space_id");

    if (shouldCreate && spaceId) {
      setPreselectedSpaceId(spaceId);
      setSelectedSpaceId(spaceId); // Also set for price auto-population
      setCreateOpen(true);
      // Clean up URL params
      window.history.replaceState({}, "", "/agreements");
    }
  }, [searchParams]);

  // Compute price based on space and agreement type
  const computePrice = (spaceId: string | null, agreementType: string | null): number | null => {
    if (!spaceId || !agreementType) return null;

    const space = spaces.find((s) => s.id === spaceId);
    if (!space) return null;

    switch (agreementType) {
      case "daily":
        return space.effective_daily_price;
      case "monthly":
        return space.effective_monthly_price;
      case "quarterly":
        return space.effective_monthly_price ? space.effective_monthly_price * 3 : null;
      case "yearly":
        return space.effective_monthly_price ? space.effective_monthly_price * 12 : null;
      default:
        return null;
    }
  };

  // Auto-populate price when space or agreement type changes
  useEffect(() => {
    const price = computePrice(selectedSpaceId, selectedAgreementType);
    if (price !== null) {
      setPriceValue(price.toString());
    }
  }, [selectedSpaceId, selectedAgreementType, spaces]);

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const body = {
      customer_id: form.get("customer_id") as string,
      space_id: form.get("space_id") as string,
      agreement_type: form.get("agreement_type") as string,
      start_date: form.get("start_date") as string,
      price: Number(form.get("price")),
      license_plates: form.get("license_plates") as string,
      notes: (form.get("notes") as string) || null,
    };
    try {
      await api.post("/api/v1/agreements", body);
      toast.success("合約已建立");
      setCreateOpen(false);
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  const handleTerminate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!terminateId) return;
    const form = new FormData(e.currentTarget);
    try {
      await api.post(`/api/v1/agreements/${terminateId}/terminate`, {
        termination_reason: form.get("reason") as string,
      });
      toast.success("合約已終止");
      setTerminateId(null);
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">
          合約管理
          {customerIdParam && <span className="text-base text-muted-foreground ml-2">(篩選客戶)</span>}
        </h2>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>新增合約</Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>新增合約</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>客戶</Label>
                  <Select name="customer_id" required defaultValue={customerIdParam || undefined}>
                    <SelectTrigger><SelectValue placeholder="選擇客戶" /></SelectTrigger>
                    <SelectContent>
                      {customers.map((c) => (
                        <SelectItem key={c.id} value={c.id}>{c.name} ({c.phone})</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>車位</Label>
                  <Select
                    name="space_id"
                    required
                    defaultValue={preselectedSpaceId || undefined}
                    onValueChange={(value) => setSelectedSpaceId(value)}
                  >
                    <SelectTrigger><SelectValue placeholder="選擇車位" /></SelectTrigger>
                    <SelectContent>
                      {spaces
                        .sort((a, b) => {
                          // Show available spaces first
                          if (a.computed_status === "available" && b.computed_status !== "available") return -1;
                          if (a.computed_status !== "available" && b.computed_status === "available") return 1;
                          return (a.site_name || "").localeCompare(b.site_name || "");
                        })
                        .map((s) => (
                          <SelectItem key={s.id} value={s.id}>
                            <span className="flex items-center gap-2">
                              <span>{s.site_name} / {s.name}</span>
                              {s.computed_status === "occupied" && (
                                <span className="text-xs text-muted-foreground">(目前已占用)</span>
                              )}
                              {s.computed_status === "available" && (
                                <span className="text-xs text-green-600">✓ 可用</span>
                              )}
                            </span>
                          </SelectItem>
                        ))
                      }
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    可選擇未來日期預約車位（系統會檢查日期是否重疊）
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>合約類型</Label>
                  <Select name="agreement_type" required onValueChange={(value) => setSelectedAgreementType(value)}>
                    <SelectTrigger><SelectValue placeholder="選擇類型" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="monthly">月租</SelectItem>
                      <SelectItem value="quarterly">季租</SelectItem>
                      <SelectItem value="yearly">年租</SelectItem>
                      <SelectItem value="daily">日租</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="start_date">起始日期</Label>
                  <Input id="start_date" name="start_date" type="date" required />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="price">金額</Label>
                  <Input
                    id="price"
                    name="price"
                    type="number"
                    min="0"
                    required
                    value={priceValue}
                    onChange={(e) => setPriceValue(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    系統已根據車位及合約類型自動填入，可手動調整
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="license_plates">車牌號碼</Label>
                  <Input id="license_plates" name="license_plates" placeholder="ABC-1234" required />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="notes">備註</Label>
                <Input id="notes" name="notes" />
              </div>
              <Button type="submit" className="w-full">建立合約</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">有效合約</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{summary.active_count} <span className="text-sm font-normal text-muted-foreground">筆</span></p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">待收繳費 (未付)</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{formatCurrency(summary.pending_payment_total)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">可用車位</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{summary.available_space_count} <span className="text-sm font-normal text-muted-foreground">個</span></p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">逾期</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{summary.overdue_count} <span className="text-sm font-normal text-muted-foreground">筆</span></p>
            </CardContent>
          </Card>
        </div>
      )}

      {loading ? (
        <p className="text-muted-foreground">載入中...</p>
      ) : agreements.length === 0 ? (
        <p className="text-muted-foreground">尚無合約資料</p>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>客戶</TableHead>
                <TableHead>車位</TableHead>
                <TableHead>類型</TableHead>
                <TableHead>起始日</TableHead>
                <TableHead>結束日</TableHead>
                <TableHead>金額</TableHead>
                <TableHead>車牌</TableHead>
                <TableHead>付款狀態</TableHead>
                <TableHead>合約狀態</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {agreements.map((a) => (
                <TableRow key={a.id}>
                  <TableCell>
                    <Link href={`/customers/${a.customer_id}`} className="font-medium text-primary hover:underline">
                      {a.customer_name}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Link href={`/agreements/${a.id}`} className="hover:underline">
                      {a.space_name}
                    </Link>
                  </TableCell>
                  <TableCell>{agreementTypeLabel(a.agreement_type)}</TableCell>
                  <TableCell>{formatDate(a.start_date)}</TableCell>
                  <TableCell>{formatDate(a.end_date)}</TableCell>
                  <TableCell>{formatCurrency(a.price)}</TableCell>
                  <TableCell className="font-mono text-sm">{a.license_plates}</TableCell>
                  <TableCell>
                    <Badge variant={
                      a.payment_status === "completed" ? "default" :
                      a.payment_status === "voided" ? "destructive" :
                      "secondary"
                    }>
                      {paymentStatusLabel(a.payment_status || "pending")}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {a.terminated_at ? (
                      <Badge variant="destructive">已終止</Badge>
                    ) : (
                      <Badge variant="default">有效</Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    {!a.terminated_at && (
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => setTerminateId(a.id)}
                      >
                        終止
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Terminate dialog */}
      <Dialog open={!!terminateId} onOpenChange={(open) => { if (!open) setTerminateId(null); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>終止合約</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleTerminate} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="reason">終止原因</Label>
              <Input id="reason" name="reason" placeholder="請輸入終止原因" required />
            </div>
            <Button type="submit" variant="destructive" className="w-full">確認終止</Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
