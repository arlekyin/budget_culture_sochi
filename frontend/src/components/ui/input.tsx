import { cn } from '@/lib/utils'

type InputProps = React.InputHTMLAttributes<HTMLInputElement>

export function Input({ className, type, ...props }: InputProps) {
  return (
    <input
      type={type}
      className={cn(
        'flex h-9 w-full rounded-md border border-gray-200 bg-white px-3 py-1 text-sm shadow-sm',
        'placeholder:text-gray-400',
        'focus:outline-none focus:ring-2 focus:ring-[#5e6ad2] focus:border-transparent',
        'disabled:cursor-not-allowed disabled:opacity-50',
        'transition-colors',
        className
      )}
      {...props}
    />
  )
}
