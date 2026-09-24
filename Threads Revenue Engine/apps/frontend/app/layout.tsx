import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Threads Revenue Engine', description: 'Mock-first content operations workspace' };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="ko"><body>{children}</body></html>; }
