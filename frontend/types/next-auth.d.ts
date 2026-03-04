import "next-auth";
import "next-auth/jwt";

declare module "next-auth" {
  interface User {
    id: string;
    email: string;
    accessToken: string;
    profile?: {
      age?: number;
      gender?: string;
      name?: string;
    };
  }

  interface Session {
    user: {
      id: string;
      email: string;
      accessToken: string;
      profile?: {
        age?: number;
        gender?: string;
        name?: string;
      };
    };
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string;
    accessToken: string;
    profile?: {
      age?: number;
      gender?: string;
      name?: string;
    };
  }
}
