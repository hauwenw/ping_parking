"use client";

import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-background px-4">
      <SidebarTrigger />
      <div className="flex-1" />
      {user && (
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">{user.display_name}</span>
          <Button variant="outline" size="sm" onClick={logout}>
            登出
          </Button>
        </div>
      )}
    </header>
  );
}
