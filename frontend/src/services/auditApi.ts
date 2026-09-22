import api from "./api";

export type AuditLog = {
  id: string;
  user_id: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  details: string | null;
  ip_address: string | null;
  created_at: string;
};

export async function listAuditLogs(action?: string): Promise<AuditLog[]> {
  const response = await api.get<AuditLog[]>("/audit/logs", {
    params: action ? { action } : undefined,
  });
  return response.data;
}
