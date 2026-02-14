/** Format phone: 0912345678 → 0912-345-678 */
export function formatPhone(phone: string): string {
  if (phone.length !== 10) return phone;
  return `${phone.slice(0, 4)}-${phone.slice(4, 7)}-${phone.slice(7)}`;
}

/** Format currency: 3600 → NT$3,600 */
export function formatCurrency(amount: number): string {
  return `NT$${amount.toLocaleString("en-US")}`;
}

/** Format date: 2026-03-01 → 2026年03月01日 */
export function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}年${m}月${day}日`;
}

/** Agreement type label */
export function agreementTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    daily: "日租",
    monthly: "月租",
    quarterly: "季租",
    yearly: "年租",
  };
  return labels[type] || type;
}

/** Space status label */
export function spaceStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    available: "可用",
    occupied: "已占用",
    reserved: "已預約",
    maintenance: "維護中",
  };
  return labels[status] || status;
}

/** Payment status label */
export function paymentStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: "待付款",
    completed: "已付款",
    voided: "已作廢",
  };
  return labels[status] || status;
}
