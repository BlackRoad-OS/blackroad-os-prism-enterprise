import clsx from "clsx";
import { Slot } from "@radix-ui/react-slot";
import { ButtonHTMLAttributes } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
  asChild?: boolean;
};

export function Button({ variant = "primary", asChild = false, className, ...props }: ButtonProps) {
  const baseStyles = "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2";
  const variants: Record<NonNullable<ButtonProps["variant"]>, string> = {
    primary: "bg-slate-900 text-white hover:bg-slate-700 focus-visible:ring-slate-500",
    secondary: "bg-white text-slate-900 ring-1 ring-slate-200 hover:bg-slate-100 focus-visible:ring-slate-400"
  };
  const Component: any = asChild ? Slot : "button";

  return <Component className={clsx(baseStyles, variants[variant], className)} {...props} />;
}
