import { type NextRequest, NextResponse } from "next/server";
import { downloadSyncData } from "@/lib/blob";
import { getUserByToken } from "@/lib/redis";
import { SyncDataSchema } from "@/lib/schemas";
import type { ApiResponse } from "@/types";
import { z } from "zod";

export async function GET(request: NextRequest) {
  try {
    // Get API token from Authorization header
    const authHeader = request.headers.get("Authorization");
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json<ApiResponse>(
        {
          success: false,
          error: "Missing or invalid Authorization header",
        },
        { status: 401 }
      );
    }

    const token = authHeader.substring(7); // Remove "Bearer " prefix

    // Verify token and get user
    const user = await getUserByToken(token);
    if (!user) {
      return NextResponse.json<ApiResponse>(
        {
          success: false,
          error: "Invalid API token",
        },
        { status: 401 }
      );
    }

    // Download from Vercel Blob
    const rawData = await downloadSyncData(user.email);

    if (!rawData) {
      return NextResponse.json<ApiResponse>(
        {
          success: false,
          error: "No sync data found",
        },
        { status: 404 }
      );
    }

    // Validate the downloaded data matches TUI format
    const syncData = SyncDataSchema.parse(rawData);

    return NextResponse.json<ApiResponse>(
      {
        success: true,
        data: syncData,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Download error:", error);

    // Handle Zod validation errors with detailed messages
    if (error instanceof z.ZodError) {
      const errorMessages = error.issues
        .map((e) => `${e.path.join(".")}: ${e.message}`)
        .join(", ");
      return NextResponse.json<ApiResponse>(
        {
          success: false,
          error: `Stored data has invalid structure: ${errorMessages}`,
        },
        { status: 500 }
      );
    }

    return NextResponse.json<ApiResponse>(
      {
        success: false,
        error: "Internal server error",
      },
      { status: 500 }
    );
  }
}
