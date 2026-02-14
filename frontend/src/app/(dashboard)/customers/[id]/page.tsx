"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import type { Customer, Agreement } from "@/lib/types";
import {
  formatPhone,
  formatCurrency,
  formatDate,
  agreementTypeLabel,
  paymentStatusLabel,
} from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { toast } from "sonner";

export default function CustomerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const customerId = params.id as string;

  const [customer, setCustomer] = useState<Customer | null>(null);
  const [agreements, setAgreements] = useState<Agreement[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [customerData, agreementsData] = await Promise.all([
        api.get<Customer>(`/api/v1/customers/${customerId}`),
        api.get<Agreement[]>(`/api/v1/agreements?customer_id=${customerId}`),
      ]);
      setCustomer(customerData);
      setAgreements(agreementsData);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        toast.error("找不到客戶");
        router.push("/customers");
        return;
      }
    } finally {
      setLoading(false);
    }
  }, [customerId, router]);

  useEffect(() => { load(); }, [load]);

  if (loading) {
    return <p className="text-muted-foreground p-6">載入中...</p>;
  }

  if (!customer) return null;

  return (
    <div className="space-y-6">
      {/* Breadcrumb & header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            <Link href="/customers" className="hover:underline">客戶管理</Link>
            {" > "}客戶詳情
          </p>
          <div className="flex items-center gap-3 mt-1">
            <h2 className="text-2xl font-bold">{customer.name}</h2>
            <Badge>{customer.active_agreement_count} 有效合約</Badge>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => router.push("/customers")}>返回列表</Button>
          <Link href={`/agreements?customer_id=${customerId}`}>
            <Button>新增合約</Button>
          </Link>
        </div>
      </div>

      <Tabs defaultValue="info">
        <TabsList>
          <TabsTrigger value="info">基本資料</TabsTrigger>
          <TabsTrigger value="agreements">合約記錄</TabsTrigger>
        </TabsList>

        <TabsContent value="info" className="mt-4">
          <Card>
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">姓名</p>
                  <p className="font-medium">{customer.name}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">電子郵件</p>
                  <p>{customer.email || "-"}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">電話</p>
                  <p>{formatPhone(customer.phone)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">有效合約</p>
                  <p>{customer.active_agreement_count} 筆</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">聯絡電話</p>
                  <p>{customer.contact_phone ? formatPhone(customer.contact_phone) : "-"}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">備註</p>
                  <p>{customer.notes || "-"}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agreements" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>合約記錄</CardTitle>
            </CardHeader>
            <CardContent>
              {agreements.length === 0 ? (
                <p className="text-muted-foreground">尚無合約記錄</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>車位</TableHead>
                      <TableHead>類型</TableHead>
                      <TableHead>合約期間</TableHead>
                      <TableHead>金額</TableHead>
                      <TableHead>付款狀態</TableHead>
                      <TableHead>合約狀態</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {agreements.map((a) => (
                      <TableRow key={a.id}>
                        <TableCell>
                          <Link
                            href={`/agreements/${a.id}`}
                            className="font-medium text-primary hover:underline"
                          >
                            {a.space_name}
                          </Link>
                        </TableCell>
                        <TableCell>{agreementTypeLabel(a.agreement_type)}</TableCell>
                        <TableCell>
                          {formatDate(a.start_date)} ~ {formatDate(a.end_date)}
                        </TableCell>
                        <TableCell>{formatCurrency(a.price)}</TableCell>
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
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
