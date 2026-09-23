const backendUrl =
  process.env.BACKEND_INTERNAL_URL ||
  (process.env.NODE_ENV === "production"
    ? "http://backend:8000/api/v1/:path*"
    : "http://127.0.0.1:8000/api/v1/:path*");

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: backendUrl,
      },
    ];
  },
};

module.exports = nextConfig;

