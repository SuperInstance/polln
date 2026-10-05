/**
 * Vendor module declarations for OPTIONAL integrations.
 *
 * These modules are imported by optional feature surfaces (cloud KMS
 * providers, admin UI kits, observability exporters, server middleware)
 * but are NOT dependencies of this package — the code paths are opt-in
 * at runtime and the packages are expected to be installed only where
 * those features are used.
 *
 * Declarations below are MINIMAL STRUCTURAL types covering exactly what
 * this repo consumes (plan Category 1, TYPESCRIPT_FIX_PLAN "Option B"),
 * so namespace-style usage (`pg.Pool` as a type) typechecks correctly.
 * If one of these becomes a real dependency, delete its entry here and
 * use the package's own types.
 *
 * NOTE: d3 / chart.js / react-chartjs-2 are typed via devDependencies
 * (@types/d3 + the packages' bundled types) — do not add them here.
 */

// ---------------------------------------------------------------------------
// AWS (KMS + S3 secret/backup providers)
// ---------------------------------------------------------------------------
declare module '@aws-sdk/client-kms' {
  export class KMSClient {
    constructor(config?: { region?: string });
    send(command: unknown): Promise<Record<string, unknown>>;
  }
  export class EncryptCommand {
    constructor(input: Record<string, unknown>);
  }
  export class DecryptCommand {
    constructor(input: Record<string, unknown>);
  }
}
declare module '@aws-sdk/client-s3' {
  export class S3Client {
    constructor(config?: { region?: string });
    send(command: unknown): Promise<Record<string, unknown>>;
  }
  export class PutObjectCommand {
    constructor(input: Record<string, unknown>);
  }
  export class GetObjectCommand {
    constructor(input: Record<string, unknown>);
  }
  export class DeleteObjectCommand {
    constructor(input: Record<string, unknown>);
  }
  export class ListObjectsV2Command {
    constructor(input: Record<string, unknown>);
  }
}

// ---------------------------------------------------------------------------
// Azure + GCP (KeyVault / KMS secret providers)
// ---------------------------------------------------------------------------
declare module '@azure/identity' {
  export class DefaultAzureCredential {
    getToken(scopes: string | string[]): Promise<{ token: string; expiresOnTimestamp: number }>;
  }
}
declare module '@azure/keyvault-secrets' {
  export class SecretClient {
    constructor(vaultUrl: string, credential: unknown);
    getSecret(name: string): Promise<{ value: string | undefined; name: string; properties: unknown }>;
    setSecret(name: string, value: string): Promise<{ name: string; properties: unknown }>;
    deleteSecret(name: string): Promise<unknown>;
  }
}
declare module '@azure/keyvault-keys' {
  export class KeyClient {
    constructor(vaultUrl: string, credential: unknown);
    getKey(name: string): Promise<{ key: unknown; name: string }>;
  }
  export class CryptographyClient {
    constructor(key: unknown, credential?: unknown);
    encrypt(options: Record<string, unknown>): Promise<{ result: Uint8Array }>;
    decrypt(options: Record<string, unknown>): Promise<{ result: Uint8Array }>;
  }
}
declare module '@google-cloud/kms' {
  export class KeyManagementServiceClient {
    constructor(options?: { projectId?: string; keyFilename?: string });
    encrypt(request: Record<string, unknown>): Promise<[{ ciphertext: Buffer }]>;
    decrypt(request: Record<string, unknown>): Promise<[{ plaintext: Buffer }]>;
  }
}

// ---------------------------------------------------------------------------
// Server middleware (optional express hardening)
// ---------------------------------------------------------------------------
declare module 'cors' {
  const cors: (options?: Record<string, unknown>) => (req: unknown, res: unknown, next: () => void) => void;
  export default cors;
}
declare module 'helmet' {
  const helmet: (options?: Record<string, unknown>) => (req: unknown, res: unknown, next: () => void) => void;
  export default helmet;
}
declare module 'morgan' {
  const morgan: {
    (format: string, options?: Record<string, unknown>): (req: unknown, res: unknown, next: () => void) => void;
    token(name: string, fn: (req: unknown, res: unknown) => string): void;
  };
  export default morgan;
}
declare module 'express-rate-limit' {
  const rateLimit: (options?: { windowMs?: number; max?: number; message?: unknown }) => (req: unknown, res: unknown, next: () => void) => void;
  export default rateLimit;
}

// ---------------------------------------------------------------------------
// Admin UI kits (optional admin panels)
// ---------------------------------------------------------------------------
declare module 'antd';
declare module '@ant-design/icons';
declare module '@mui/material';
declare module '@mui/icons-material';
declare module '@mui/x-date-pickers/LocalizationProvider';
declare module '@mui/x-date-pickers/DatePicker';
declare module '@mui/x-date-pickers/AdapterDateFns';
declare module 'styled-components';

// Visualization (d3 / chart.js / react-chartjs-2): intentionally NOT declared
// here. The visualization components consume rich d3 chart types; minimal
// declarations would type as `any` and real @types/d3 surfaces ~350 latent
// errors in those files. They stay unresolved until the UI batch fixes them
// with real types (@types/d3 + chart.js bundled types as devDeps).

// Date handling
declare module 'date-fns';

// Testing utilities referenced from component sources
declare module '@testing-library/react';

// Remote ESM CDN import (mathlive, loaded at runtime in the browser)
declare module 'https://unpkg.com/mathlive@0.90.0/dist/mathlive.mjs';
