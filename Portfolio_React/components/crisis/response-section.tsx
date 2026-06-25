"use client"

import { Check, Copy, Hash, Send, UserCog } from "lucide-react"
import { useState } from "react"
import type { CrisisData } from "@/lib/crisis-data"

function MessageCard({ index, text }: { index: number; text: string }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    } catch {
      setCopied(false)
    }
  }

  return (
    <article className="group flex flex-col rounded-2xl border border-border bg-card/60 p-5 transition-colors hover:border-primary/40">
      <div className="flex items-center justify-between">
        <span className="inline-flex items-center gap-2 font-mono text-xs text-muted-foreground">
          <span className="flex size-6 items-center justify-center rounded-md bg-primary/15 text-primary">
            {index + 1}
          </span>
          Proposition
        </span>
        <button
          type="button"
          onClick={handleCopy}
          aria-label={`Copier la proposition ${index + 1}`}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border px-2.5 py-1.5 text-xs font-medium text-muted-foreground transition-all hover:border-primary/50 hover:text-foreground active:scale-95"
        >
          {copied ? (
            <>
              <Check className="size-3.5 text-success" />
              Copié
            </>
          ) : (
            <>
              <Copy className="size-3.5" />
              Copier
            </>
          )}
        </button>
      </div>
      <p className="mt-4 text-sm leading-relaxed text-foreground/90 text-pretty">
        {text}
      </p>
    </article>
  )
}

export function ResponseSection({
  response,
}: {
  response: CrisisData["response"]
}) {
  return (
    <section
      aria-label="Riposte proposée"
      className="animate-rise"
      style={{ animationDelay: "160ms" }}
    >
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Send className="size-4 text-primary" />
          <h2 className="text-base font-semibold text-foreground">
            La riposte
          </h2>
          <span className="inline-flex items-center gap-1 rounded-full border border-border bg-secondary px-2.5 py-0.5 font-mono text-xs text-muted-foreground">
            <Hash className="size-3" />
            canal {response.channel}
          </span>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-warning/30 bg-warning/10 px-3 py-1 text-xs font-medium text-warning">
          <UserCog className="size-3.5" />
          À valider par un humain
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {response.messages.map((text, i) => (
          <MessageCard key={i} index={i} text={text} />
        ))}
      </div>
    </section>
  )
}
