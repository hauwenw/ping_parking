"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { SystemLog } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const actionLabels: Record<string, string> = {
  LOGIN: "登入",
  LOGOUT: "登出",
  FAILED_LOGIN: "登入失敗",
  CREATE: "新增",
  UPDATE: "更新",
  DELETE: "刪除",
};

export default function SystemLogsPage() {
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<SystemLog[]>("/api/v1/system-logs?limit=100").then((data) => {
      setLogs(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">系統紀錄</h2>
        <Button
          variant="outline"
          onClick={async () => {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const token = api.getToken();
            const res = await fetch(`${API_URL}/api/v1/system-logs/export?limit=1000`, {
              headers: token ? { Authorization: `Bearer ${token}` } : {},
            });
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "system_logs.csv";
            a.click();
            URL.revokeObjectURL(url);
          }}
        >
          匯出 CSV
        </Button>
      </div>

      {loading ? (
        <p className="text-muted-foreground">載入中...</p>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>時間</TableHead>
                <TableHead>操作</TableHead>
                <TableHead>資料表</TableHead>
                <TableHead>IP</TableHead>
                <TableHead>變更內容</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="text-sm whitespace-nowrap">
                    {new Date(log.created_at).toLocaleString("zh-TW")}
                  </TableCell>
                  <TableCell>
                    <Badge variant={
                      log.action === "DELETE" ? "destructive" :
                      log.action === "CREATE" ? "default" :
                      "secondary"
                    }>
                      {actionLabels[log.action] || log.action}
                    </Badge>
                  </TableCell>
                  <TableCell>{log.table_name || "-"}</TableCell>
                  <TableCell className="font-mono text-xs">{log.ip_address || "-"}</TableCell>
                  <TableCell className="max-w-xs truncate text-xs text-muted-foreground">
                    {log.new_values ? JSON.stringify(log.new_values) : "-"}
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
