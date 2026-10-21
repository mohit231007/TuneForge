import "./globals.css";
import Shell from "@/components/Shell";

export const metadata = {
  title: "TuneForge Studio",
  description: "Self-service LoRA and QLoRA experimentation, evaluation, and adapter lifecycle management.",
};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="en">
      <body>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
