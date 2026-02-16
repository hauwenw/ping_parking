"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import type { Agreement, Payment } from "@/lib/types";
import {
  formatCurrency,
  formatDate,
  agreementTypeLabel,
  paymentStatusLabel,
} from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from "sonner";

export default function AgreementDetailPage() {
  const params = useParams();
  const router = useRouter();
  const agreementId = params.id as string;

  const [agreement, setAgreement] = useState<Agreement | null>(null);
  const [payment, setPayment] = useState<Payment | null>(null);
  const [loading, setLoading] = useState(true);
  const [terminateOpen, setTerminateOpen] = useState(false);
  const [completeOpen, setCompleteOpen] = useState(false);
  const [editPaymentOpen, setEditPaymentOpen] = useState(false);

  const load = useCallback(async () => {
    try {
      const [agreeData, paymentData] = await Promise.all([
        api.get<Agreement>(`/api/v1/agreements/${agreementId}`),
        api.get<Payment>(`/api/v1/agreements/${agreementId}/payment`).catch(() => null),
      ]);
      setAgreement(agreeData);
      setPayment(paymentData);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        toast.error("找不到合約");
        router.push("/agreements");
        return;
      }
    } finally {
      setLoading(false);
    }
  }, [agreementId, router]);

  useEffect(() => { load(); }, [load]);

  const handleTerminate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    try {
      await api.post(`/api/v1/agreements/${agreementId}/terminate`, {
        termination_reason: form.get("reason") as string,
      });
      toast.success("合約已終止");
      setTerminateOpen(false);
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  const handleCompletePayment = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!payment) return;
    const form = new FormData(e.currentTarget);
    try {
      await api.post(`/api/v1/payments/${payment.id}/complete`, {
        bank_reference: form.get("bank_reference") as string,
        notes: (form.get("notes") as string) || null,
      });
      toast.success("已記錄付款");
      setCompleteOpen(false);
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  const handleEditPayment = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!payment) return;
    const form = new FormData(e.currentTarget);
    try {
      await api.put(`/api/v1/payments/${payment.id}`, {
        amount: Number(form.get("amount")),
        status: form.get("status") as string,
        payment_date: (form.get("payment_date") as string) || null,
        due_date: (form.get("due_date") as string) || null,
        bank_reference: (form.get("bank_reference") as string) || null,
        notes: (form.get("notes") as string) || null,
      });
      toast.success("付款已更新");
      setEditPaymentOpen(false);
      await load();
    } catch (err) {
      if (err instanceof ApiError) toast.error(err.message);
    }
  };

  if (loading) {
    return <p className="text-muted-foreground p-6">載入中...</p>;
  }

  if (!agreement) return null;

  return (
    <div className="space-y-6">
      {/* Breadcrumb & header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            <Link href="/agreements" className="hover:underline">合約管理</Link>
            {" > "}合約詳情
          </p>
          <div className="flex items-center gap-3 mt-1">
            <h2 className="text-2xl font-bold">
              合約 {agreementId.slice(0, 8).toUpperCase()}
            </h2>
            {agreement.terminated_at ? (
              <Badge variant="destructive">已終止</Badge>
            ) : (
              <Badge variant="default">有效</Badge>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          {!agreement.terminated_at && (
            <Button variant="destructive" onClick={() => setTerminateOpen(true)}>
              終止合約
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Customer & Space Info */}
        <Card>
          <CardHeader>
            <CardTitle>客戶與車位資訊</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">客戶</p>
                <Link
                  href={`/customers/${agreement.customer_id}`}
                  className="font-medium text-primary hover:underline"
                >
                  {agreement.customer_name}
                </Link>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">車位</p>
                <p className="font-medium">{agreement.space_name}</p>
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">車牌號碼</p>
              <p className="font-mono">{agreement.license_plates}</p>
            </div>
          </CardContent>
        </Card>

        {/* Agreement Info */}
        <Card>
          <CardHeader>
            <CardTitle>合約資訊</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">類型</p>
                <p>{agreementTypeLabel(agreement.agreement_type)}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">合約期間</p>
                <p>{formatDate(agreement.start_date)} 至 {formatDate(agreement.end_date)}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">金額</p>
                <p className="text-lg font-bold">{formatCurrency(agreement.price)}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">備註</p>
                <p>{agreement.notes || "-"}</p>
              </div>
            </div>
            {agreement.terminated_at && (
              <div className="border-t pt-4 space-y-2">
                <p className="text-sm text-muted-foreground">終止原因</p>
                <p className="text-destructive">{agreement.termination_reason}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Payment Info */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>付款資訊</CardTitle>
          {payment && (
            <div className="space-x-2">
              {payment.status === "pending" && (
                <Button onClick={() => setCompleteOpen(true)}>記錄付款</Button>
              )}
              <Button variant="outline" onClick={() => setEditPaymentOpen(true)}>編輯付款</Button>
            </div>
          )}
        </CardHeader>
        <CardContent>
          {payment ? (
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">付款狀態</p>
                <Badge variant={
                  payment.status === "completed" ? "default" :
                  payment.status === "voided" ? "destructive" :
                  "secondary"
                }>
                  {paymentStatusLabel(payment.status)}
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">應付日期</p>
                <p>{payment.due_date ? formatDate(payment.due_date) : "-"}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">應付金額</p>
                <p className="font-bold">{formatCurrency(payment.amount)}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">付款日期</p>
                <p>{payment.payment_date ? formatDate(payment.payment_date) : "-"}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">銀行參考號</p>
                <p className="font-mono text-sm">{payment.bank_reference || "-"}</p>
              </div>
              {payment.notes && (
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">備註</p>
                  <p className="text-sm">{payment.notes}</p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-muted-foreground">無付款記錄</p>
          )}
        </CardContent>
      </Card>

      {/* Terminate dialog */}
      <Dialog open={terminateOpen} onOpenChange={setTerminateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>終止合約</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleTerminate} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="reason">終止原因</Label>
              <Input id="reason" name="reason" required />
            </div>
            <Button type="submit" variant="destructive" className="w-full">確認終止</Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Complete payment dialog */}
      <Dialog open={completeOpen} onOpenChange={setCompleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>記錄付款</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCompletePayment} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="bank_reference">銀行參考號</Label>
              <Input id="bank_reference" name="bank_reference" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="notes">備註</Label>
              <Input id="notes" name="notes" />
            </div>
            <Button type="submit" className="w-full">確認付款</Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit payment dialog */}
      {payment && (
        <Dialog open={editPaymentOpen} onOpenChange={setEditPaymentOpen}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>編輯付款</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleEditPayment} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="edit_amount">金額 (NT$)</Label>
                <Input
                  id="edit_amount"
                  name="amount"
                  type="number"
                  min={0}
                  required
                  defaultValue={payment.amount}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit_status">狀態</Label>
                <Select name="status" required defaultValue={payment.status}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">待付款</SelectItem>
                    <SelectItem value="completed">已付款</SelectItem>
                    <SelectItem value="voided">已作廢</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit_due_date">應付日期</Label>
                <Input
                  id="edit_due_date"
                  name="due_date"
                  type="date"
                  defaultValue={payment.due_date || (agreement ? agreement.start_date : "")}
                />
                <p className="text-xs text-muted-foreground">
                  預設為合約開始日期，可手動調整
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit_payment_date">付款日期</Label>
                <Input
                  id="edit_payment_date"
                  name="payment_date"
                  type="date"
                  defaultValue={payment.payment_date || ""}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit_bank_reference">銀行參考號</Label>
                <Input
                  id="edit_bank_reference"
                  name="bank_reference"
                  maxLength={100}
                  defaultValue={payment.bank_reference || ""}
                  placeholder="轉帳單號或參考號碼"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit_notes">備註</Label>
                <Textarea
                  id="edit_notes"
                  name="notes"
                  rows={3}
                  defaultValue={payment.notes || ""}
                  placeholder="付款備註（選填）"
                />
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setEditPaymentOpen(false)}>
                  取消
                </Button>
                <Button type="submit">儲存</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
