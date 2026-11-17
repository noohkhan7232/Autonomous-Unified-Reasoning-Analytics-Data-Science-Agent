import type { Metadata } from "next";
import "./workspace.css";

export const metadata: Metadata = {
  title: "AURA-DS | Analytics Workspace",
  description: "Autonomous reasoning and analytics workspace",
};

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
