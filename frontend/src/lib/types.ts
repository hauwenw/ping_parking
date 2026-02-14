export interface Site {
  id: string;
  name: string;
  address: string | null;
  description: string | null;
  monthly_base_price: number;
  daily_base_price: number;
  space_count: number;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
  description: string | null;
  monthly_price: number | null;
  daily_price: number | null;
}

export interface Space {
  id: string;
  site_id: string;
  name: string;
  status: "available" | "occupied" | "reserved" | "maintenance";
  tags: string[];
  custom_price: number | null;
  site_name: string | null;
  effective_monthly_price: number | null;
  effective_daily_price: number | null;
  price_tier: "site" | "tag" | "custom" | null;
  price_tag_name: string | null;
}

export interface Customer {
  id: string;
  name: string;
  phone: string;
  contact_phone: string | null;
  email: string | null;
  notes: string | null;
  active_agreement_count: number;
}

export interface Agreement {
  id: string;
  customer_id: string;
  space_id: string;
  agreement_type: "daily" | "monthly" | "quarterly" | "yearly";
  start_date: string;
  end_date: string;
  price: number;
  license_plates: string;
  notes: string | null;
  terminated_at: string | null;
  termination_reason: string | null;
  customer_name: string | null;
  space_name: string | null;
  payment_status: string | null;
}

export interface Payment {
  id: string;
  agreement_id: string;
  amount: number;
  status: "pending" | "completed" | "voided";
  payment_date: string | null;
  bank_reference: string | null;
  notes: string | null;
}

export interface AgreementSummary {
  active_count: number;
  pending_payment_total: number;
  available_space_count: number;
  overdue_count: number;
}

export interface SystemLog {
  id: string;
  user_id: string | null;
  action: string;
  table_name: string | null;
  record_id: string | null;
  old_values: Record<string, unknown> | null;
  new_values: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_email: string;
  user_name: string;
}

export interface UserInfo {
  id: string;
  email: string;
  display_name: string;
}
