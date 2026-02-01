// Mock data layer for StudyHub
// Simulates Supabase responses - will be replaced with real API calls

export interface Platform {
  id: string;
  name: string;
  icon: string;
  color: string;
  count: number;
  label: string;
}

export interface Deadline {
  id: string;
  title: string;
  course: string;
  platform: 'canvas' | 'gradescope' | 'campuswire' | 'prairielearn';
  type: string;
  dueDate: string;
  dueTime: string;
  status: 'pending' | 'submitted' | 'graded';
}

export interface ScheduleItem {
  id: string;
  title: string;
  type: 'class' | 'study' | 'break' | 'office_hours';
  startTime: string;
  duration: string;
  location?: string;
  color: string;
  isActive?: boolean;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

// Mock user data
export const mockUser: User = {
  id: 'user_123',
  name: 'Alex',
  email: 'alex@illinois.edu',
};

// Mock platform summaries
export const mockPlatforms: Platform[] = [
  {
    id: 'canvas',
    name: 'Canvas',
    icon: 'book',
    color: '#e74c3c',
    count: 4,
    label: 'pending tasks',
  },
  {
    id: 'gradescope',
    name: 'Gradescope',
    icon: 'clipboard',
    color: '#27ae60',
    count: 2,
    label: 'submissions due',
  },
  {
    id: 'campuswire',
    name: 'Campuswire',
    icon: 'message',
    color: '#3498db',
    count: 8,
    label: 'new posts',
  },
];

// Mock deadlines
export const mockDeadlines: Deadline[] = [
  {
    id: '1',
    title: 'Problem Set 4: Dynamic Programming',
    course: 'CS 101 - Intro to Computer Science',
    platform: 'canvas',
    type: 'Assignment',
    dueDate: 'Feb 4',
    dueTime: '11:59 PM',
    status: 'pending',
  },
  {
    id: '2',
    title: 'Lab 5: Binary Search Trees',
    course: 'CS 101 - Intro to Computer Science',
    platform: 'gradescope',
    type: 'Coding',
    dueDate: 'Feb 5',
    dueTime: '11:59 PM',
    status: 'pending',
  },
  {
    id: '3',
    title: 'Homework 6: Integration',
    course: 'MATH 201 - Calculus II',
    platform: 'canvas',
    type: 'Homework',
    dueDate: 'Feb 6',
    dueTime: '11:59 PM',
    status: 'pending',
  },
  {
    id: '4',
    title: 'Discussion: Research Methods',
    course: 'PSYC 100 - Intro to Psychology',
    platform: 'campuswire',
    type: 'Discussion',
    dueDate: 'Feb 7',
    dueTime: '5:00 PM',
    status: 'pending',
  },
  {
    id: '5',
    title: 'Quiz 3: ML Fundamentals',
    course: 'CS 444 - Deep Learning',
    platform: 'prairielearn',
    type: 'Quiz',
    dueDate: 'Feb 8',
    dueTime: '11:59 PM',
    status: 'pending',
  },
];

// Mock schedule
export const mockSchedule: ScheduleItem[] = [
  {
    id: '1',
    title: 'CS 101 Lecture',
    type: 'class',
    startTime: '9:00 AM',
    duration: '1h 15m',
    location: 'Siebel 1404',
    color: '#3b82f6',
    isActive: false,
  },
  {
    id: '2',
    title: 'Study: Dynamic Programming',
    type: 'study',
    startTime: '10:30 AM',
    duration: '2h',
    color: '#8b5cf6',
    isActive: true,
  },
  {
    id: '3',
    title: 'Lunch Break',
    type: 'break',
    startTime: '12:30 PM',
    duration: '1h',
    color: '#6b7280',
    isActive: false,
  },
  {
    id: '4',
    title: 'MATH 201 Lecture',
    type: 'class',
    startTime: '2:00 PM',
    duration: '1h',
    location: 'Altgeld 314',
    color: '#10b981',
    isActive: false,
  },
  {
    id: '5',
    title: 'Work on CS Lab 5',
    type: 'study',
    startTime: '3:30 PM',
    duration: '2h',
    color: '#f59e0b',
    isActive: false,
  },
];

// Mock Canvas data
export const mockCanvasAssignments = [
  {
    id: '1',
    title: 'Problem Set 4: Dynamic Programming',
    course: 'CS 101 - Intro to Computer Science',
    dueDate: '2026-02-04T23:59:00Z',
    points: 100,
    submitted: false,
  },
  {
    id: '2',
    title: 'Reading Response #5',
    course: 'PSYC 100 - Intro to Psychology',
    dueDate: '2026-02-05T23:59:00Z',
    points: 20,
    submitted: false,
  },
  {
    id: '3',
    title: 'Homework 6: Integration',
    course: 'MATH 201 - Calculus II',
    dueDate: '2026-02-06T23:59:00Z',
    points: 50,
    submitted: false,
  },
  {
    id: '4',
    title: 'Group Project Proposal',
    course: 'CS 444 - Deep Learning',
    dueDate: '2026-02-10T23:59:00Z',
    points: 100,
    submitted: false,
  },
];

// Mock Gradescope data
export const mockGradescopeSubmissions = [
  {
    id: '1',
    title: 'Lab 5: Binary Search Trees',
    course: 'CS 101',
    dueDate: '2026-02-05T23:59:00Z',
    status: 'not_submitted',
    lateDays: 0,
  },
  {
    id: '2',
    title: 'MP2: Neural Networks',
    course: 'CS 444',
    dueDate: '2026-02-07T23:59:00Z',
    status: 'not_submitted',
    lateDays: 3,
  },
];

// Mock Campuswire data
export const mockCampuswirePosts = [
  {
    id: '14',
    title: 'CS 444 Canvas Question',
    preview: 'Hi, I just wanted to check if it\'s normal...',
    author: 'Anonymous',
    category: 'Lecture questions',
    postedAt: '1 day ago',
    comments: 0,
    resolved: false,
  },
  {
    id: '12',
    title: 'Difficulty expectation for mp',
    preview: 'How much time commitment and...',
    author: 'Student',
    category: 'Logistics',
    postedAt: '2 days ago',
    comments: 3,
    resolved: true,
  },
  {
    id: '11',
    title: 'Details for project guidelines?',
    preview: 'Hi Professor and TAs, I am a graduat...',
    author: 'Student',
    category: 'Logistics',
    postedAt: '2 days ago',
    comments: 2,
    resolved: true,
  },
  {
    id: '7',
    title: 'Google Colab Pro Setup',
    preview: 'I recall Professor Svetlana mentioning...',
    author: 'Zuhair Ghias',
    category: 'Lecture questions',
    postedAt: '6 days ago',
    comments: 6,
    resolved: true,
    pinned: true,
  },
  {
    id: '6',
    title: 'Office Hours Schedule (starting 1/28)',
    preview: '**Attention**: Always check Campuswire for ann...',
    author: 'Kulbir Singh Ahluwalia',
    category: 'Logistics',
    postedAt: '6 days ago',
    comments: 0,
    resolved: false,
    pinned: true,
  },
];

// API simulation functions
export async function fetchUser(): Promise<User> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 100));
  return mockUser;
}

export async function fetchPlatforms(): Promise<Platform[]> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return mockPlatforms;
}

export async function fetchDeadlines(): Promise<Deadline[]> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return mockDeadlines;
}

export async function fetchSchedule(): Promise<ScheduleItem[]> {
  await new Promise(resolve => setTimeout(resolve, 100));
  return mockSchedule;
}

export async function fetchCanvasData() {
  await new Promise(resolve => setTimeout(resolve, 100));
  return { assignments: mockCanvasAssignments };
}

export async function fetchGradescopeData() {
  await new Promise(resolve => setTimeout(resolve, 100));
  return { submissions: mockGradescopeSubmissions };
}

export async function fetchCampuswireData() {
  await new Promise(resolve => setTimeout(resolve, 100));
  return { posts: mockCampuswirePosts };
}

// Helper to get greeting based on time
export function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

// Helper to format current date
export function getFormattedDate(): string {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });
}

// Platform colors
export const platformColors: Record<string, string> = {
  canvas: '#e74c3c',
  gradescope: '#27ae60',
  campuswire: '#3498db',
  prairielearn: '#9b59b6',
};

export const platformBgColors: Record<string, string> = {
  canvas: 'bg-red-500/10 text-red-400',
  gradescope: 'bg-green-500/10 text-green-400',
  campuswire: 'bg-blue-500/10 text-blue-400',
  prairielearn: 'bg-purple-500/10 text-purple-400',
};
