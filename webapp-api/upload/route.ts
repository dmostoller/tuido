import { type NextRequest, NextResponse } from "next/server";
import { uploadSyncData } from "@/lib/blob";
import { getUserByToken, updateLastSync } from "@/lib/redis";
import { SyncDataSchema } from "@/lib/schemas";
import type { ApiResponse, SyncData } from "@/types";
import { z } from "zod";

export async function POST(request: NextRequest) {
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

    // Parse and validate request body with Zod
    const body = await request.json();
    const syncData: SyncData = SyncDataSchema.parse(body);

    // Upload to Vercel Blob
    const { url, size } = await uploadSyncData(user.email, syncData);

    // Update last sync timestamp in Redis
    await updateLastSync(user.email);

    return NextResponse.json<ApiResponse>(
      {
        success: true,
        message: "Data synced successfully",
        data: {
          url,
          size,
          timestamp: new Date().toISOString(),
        },
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Upload error:", error);

    // Handle Zod validation errors with detailed messages
    if (error instanceof z.ZodError) {
      const errorMessages = error.issues
        .map((e) => `${e.path.join(".")}: ${e.message}`)
        .join(", ");
      return NextResponse.json<ApiResponse>(
        {
          success: false,
          error: `Invalid data structure: ${errorMessages}`,
        },
        { status: 400 }
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
