import { type NextRequest, NextResponse } from "next/server";
import { checkSyncData } from "@/lib/blob";
import { getUserByToken } from "@/lib/redis";
import type { ApiResponse, SyncStatus } from "@/types";

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

    // Check sync data
    const { exists, size, uploadedAt } = await checkSyncData(user.email);

    const syncStatus: SyncStatus = {
      lastSync: user.lastSync || uploadedAt,
      dataSize: size,
    };

    return NextResponse.json<ApiResponse>(
      {
        success: true,
        data: {
          exists,
          ...syncStatus,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Check error:", error);
    return NextResponse.json<ApiResponse>(
      {
        success: false,
        error: "Internal server error",
      },
      { status: 500 }
    );
  }
}
