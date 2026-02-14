"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Agreement } from "@/lib/types";
import { formatCurrency, formatDate, agreementTypeLabel, paymentStatusLabel } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function AgreementsPage() {
  const [agreements, setAgreements] = useState<Agreement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<Agreement[]>("/api/v1/agreements").then((data) => {
      setAgreements(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">合約管理</h2>
      </div>

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
              </TableRow>
            </TableHeader>
            <TableBody>
              {agreements.map((a) => (
                <TableRow key={a.id}>
                  <TableCell className="font-medium">{a.customer_name}</TableCell>
                  <TableCell>{a.space_name}</TableCell>
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
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
