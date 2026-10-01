/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  // Browser calls /api/* on this origin; Next proxies them to the FastAPI service,
  // so there's no CORS and the API never needs to be publicly exposed.
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${process.env.API_URL ?? "http://localhost:8000"}/api/:path*` }];
  },
};
export default nextConfig;
