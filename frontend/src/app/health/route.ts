export async function GET() {
  return new Response(
    JSON.stringify({ status: "ok", service: "ocean-sentinel-frontend", version: "3.0.0" }),
    {
      headers: { "content-type": "application/json" },
    }
  );
}
