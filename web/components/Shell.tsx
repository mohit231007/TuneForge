"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Boxes,
  ChartNoAxesCombined,
  Cpu,
  GitCompareArrows,
  Hammer,
  Layers3,
  Settings2,
} from "lucide-react";
import { useEffect, useState } from "react";
import { ClientSettings, getSettings, saveSettings } from "@/lib/api";

const nav = [
  {href: "/", label: "Overview", icon: ChartNoAxesCombined},
  {href: "/experiments", label: "Experiments", icon: Cpu},
  {href: "/adapters", label: "Adapters", icon: Layers3},
  {href: "/compare", label: "Compare", icon: GitCompareArrows},
  {href: "/architecture", label: "Architecture", icon: Boxes},
];

export default function Shell({children}: {children: React.ReactNode}) {
  const pathname = usePathname();
  const [settings, setSettings] = useState<ClientSettings>({
    apiUrl: "http://localhost:8000",
    workspace: "default",
    apiKey: "",
  });

  useEffect(() => setSettings(getSettings()), []);

  function update<K extends keyof ClientSettings>(key: K, value: ClientSettings[K]) {
    const next = {...settings, [key]: value};
    setSettings(next);
    saveSettings(next);
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brandmark"><Hammer size={19}/></div>
          <div>
            <strong>TuneForge</strong>
            <span>LLM Engineering Studio</span>
          </div>
        </div>

        <nav className="nav">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link key={item.href} href={item.href} className={active ? "navitem active" : "navitem"}>
                <Icon size={18}/>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="sidebarFooter">
          <div className="sidebarTitle"><Settings2 size={15}/> Workspace</div>
          <label>
            Workspace
            <input value={settings.workspace} onChange={(e) => update("workspace", e.target.value)}/>
          </label>
          <label>
            API URL
            <input value={settings.apiUrl} onChange={(e) => update("apiUrl", e.target.value)}/>
          </label>
          <label>
            API key
            <input type="password" value={settings.apiKey} placeholder="optional locally" onChange={(e) => update("apiKey", e.target.value)}/>
          </label>
          <div className="productBy">A product by <strong>The Algosphere</strong></div>
        </div>
      </aside>

      <main className="main">{children}</main>
    </div>
  );
}
