'use client';

interface HeaderProps {
  greeting: string;
  userName: string;
  date: string;
}

export default function Header({ greeting, userName, date }: HeaderProps) {
  return (
    <header className="mb-8">
      <h1 className="text-3xl font-bold text-white">
        {greeting}, <span className="text-cyan-400">{userName}</span>
      </h1>
      <p className="text-gray-400 mt-1">{date}</p>
    </header>
  );
}
