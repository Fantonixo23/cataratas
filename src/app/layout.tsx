import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import Footer from "@/components/Footer";
import { SidebarProvider } from "@/lib/sidebar-context";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Catarata — Buscador de productos en Paraguay",
  description: "Encontrá productos de tiendas en Paraguay y consultá precios por WhatsApp.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} antialiased`}
    >
      <body className="min-h-screen bg-gray-50 text-black">
        <SidebarProvider>
          <Header />
          <div className="flex max-w-7xl mx-auto">
            <Sidebar />
            <main className="flex-1 min-w-0">
              {children}
            </main>
          </div>
          <Footer />
        </SidebarProvider>
      </body>
    </html>
  );
}
