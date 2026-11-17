import type { NextConfig } from "next";

const config: NextConfig = {
  agentRules: false,
  async rewrites() {
    return [{ source: "/api/:path*", destination: (process.env.AURA_API_URL || "http://127.0.0.1:8000") + "/api/:path*" }];
  },
};
export default config;
