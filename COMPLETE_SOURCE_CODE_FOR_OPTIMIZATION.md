# Complete AI Sim Source Code for Optimization

Generated: 2025-11-01 14:44:50

---

## App.tsx

```typescript
import React, { useState, useEffect, useMemo, useCallback, Suspense, lazy } from 'react';
import { GoogleGenAI, Type } from '@google/genai';
import { UserProfile, Tool, ChatMessage, Quest, Course, Module, Item } from './types.ts';
import { ALL_TOOLS, PRE_MADE_COURSES } from './constants.tsx';
import { triggerHapticFeedback } from './utils/mobileUtils.ts';

// Lazy load heavy components for better code splitting
const LandingPage = lazy(() => import('./components/LandingPage.tsx'));
const PricingPage = lazy(() => import('./components/PricingPage.tsx'));
const Dashboard = lazy(() => import('./components/Dashboard.tsx'));
const ToolPage = lazy(() => import('./components/ToolPage.tsx'));
const IntakeModal = lazy(() => import('./components/IntakeModal.tsx').then(m => ({ default: m.default })));
const ProfileModal = lazy(() => import('./components/ProfileModal.tsx'));
const CourseModal = lazy(() => import('./components/CourseModal.tsx'));
const CoursePlayer = lazy(() => import('./components/CoursePlayer.tsx'));
const StoreModal = lazy(() => import('./components/StoreModal.tsx'));
const LoginPage = lazy(() => import('./components/LoginPage.tsx'));
const CheckoutPage = lazy(() => import('./components/CheckoutPage.tsx'));

import type { IntakeData } from './components/IntakeModal.tsx';

// Loading fallback component
const LoadingFallback: React.FC = () => (
  <div className="min-h-screen bg-black flex items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
      <p className="text-gray-400">Loading...</p>
    </div>
  </div>
);

const shuffleArray = <T,>(array: T[]): T[] => {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
};

const generateDailyQuests = (user: UserProfile): Quest[] => {
    const potentialQuests: Omit<Quest, 'progress'>[] = [];

    const randomTool = ALL_TOOLS[Math.floor(Math.random() * ALL_TOOLS.length)];
    potentialQuests.push({
        id: `use_tool_${randomTool.id}`,
        title: `Tool Time: ${randomTool.name}`,
        description: `Utilize the ${randomTool.name} tool for a task.`,
        xpReward: 75,
        creditReward: 15,
        total: 1,
    });

    const categories: Tool['category'][] = ['Writing', 'Career', 'Wellness', 'Communication', 'Financial', 'Education'];
    const randomCategory = categories[Math.floor(Math.random() * categories.length)];
    potentialQuests.push({
        id: `use_category_${randomCategory.toLowerCase()}`,
        title: `${randomCategory} Focus`,
        description: `Use any tool from the ${randomCategory} category.`,
        xpReward: 50,
        creditReward: 10,
        total: 1,
    });

    const userCourses = user.customCourses?.filter(c => !c.userProgress?.completed);
    if (userCourses && userCourses.length > 0) {
        const randomCourse = userCourses[Math.floor(Math.random() * userCourses.length)];
        potentialQuests.push({
            id: `complete_module_${randomCourse.id}`,
            title: 'Course Progression',
            description: `Complete a module in your "${randomCourse.title}" course.`,
            xpReward: 100,
            creditReward: 20,
            total: 1,
        });
    }

    potentialQuests.push({
        id: 'use_any_3_tools',
        title: 'AI Enthusiast',
        description: 'Use any AI tool 3 times today.',
        xpReward: 120,
        creditReward: 25,
        total: 3,
    });
    
    potentialQuests.push({
        id: 'login_today',
        title: 'Daily Check-in',
        description: 'Log in to AI Sim to start your daily journey.',
        xpReward: 25,
        creditReward: 5,
        total: 1,
    });
    
    const selectedQuests = shuffleArray(potentialQuests).slice(0, 3).map(q => ({ ...q, progress: 0 }));

    const checkIn = selectedQuests.find(q => q.id === 'login_today');
    if (checkIn) {
        checkIn.progress = 1;
    }

    return selectedQuests;
};

type PlanDetails = { name: string; price: number; isAnnual: boolean; };

const App: React.FC = () => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [currentPage, setCurrentPage] = useState<'landing' | 'dashboard' | 'tool' | 'coursePlayer' | 'pricing' | 'login' | 'checkout'>('landing');
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [playingCourse, setPlayingCourse] = useState<Course | null>(null);
  const [chatHistories, setChatHistories] = useState<{ [key: string]: ChatMessage[] }>({});
  const [toolStats, setToolStats] = useState<{ [key: string]: { usage: number, streak: number } }>({});
  const [activeQuests, setActiveQuests] = useState<Quest[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<PlanDetails | null>(null);
  
  // Modal states
  const [showIntakeModal, setShowIntakeModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showCourseModal, setShowCourseModal] = useState(false);
  const [showStoreModal, setShowStoreModal] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [courseContextForTool, setCourseContextForTool] = useState<Course | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('userProfile');
    if (savedUser) {
      const loadedUser = JSON.parse(savedUser);
      setUserProfile(loadedUser);
      setCurrentPage('dashboard');

      const savedQuests = localStorage.getItem('dailyQuests');
      const savedQuestsDate = localStorage.getItem('dailyQuestsDate');
      const today = new Date().toDateString();

      if (savedQuests && savedQuestsDate === today) {
          setActiveQuests(JSON.parse(savedQuests));
      } else {
          const newQuests = generateDailyQuests(loadedUser);
          setActiveQuests(newQuests);
          localStorage.setItem('dailyQuests', JSON.stringify(newQuests));
          localStorage.setItem('dailyQuestsDate', today);
      }
    } else {
      setCurrentPage('landing');
    }
  }, []);
  
  useEffect(() => {
    if (userProfile) {
        localStorage.setItem('userProfile', JSON.stringify(userProfile));
    }
  }, [userProfile]);
  
  const handleSelectFreePlan = () => {
    setShowIntakeModal(true);
    triggerHapticFeedback();
  };
  
  const handleSelectPaidPlan = (plan: PlanDetails) => {
    setSelectedPlan(plan);
    setCurrentPage('checkout');
    triggerHapticFeedback();
  };

  const handleCheckoutSuccess = () => {
    setShowIntakeModal(true);
    setCurrentPage('landing'); // Hide checkout page behind modal
  };

  const handleNavigateToPricing = () => {
    setCurrentPage('pricing');
    triggerHapticFeedback();
  };

  const handleNavigateToLogin = () => {
    setCurrentPage('login');
    triggerHapticFeedback();
  };

  const handleLoginSuccess = () => {
    const savedUser = localStorage.getItem('userProfile');
    if (savedUser) {
      const loadedUser = JSON.parse(savedUser);
      setUserProfile(loadedUser);
      setCurrentPage('dashboard');
    } else {
      setShowIntakeModal(true);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('userProfile');
    localStorage.removeItem('dailyQuests');
    localStorage.removeItem('dailyQuestsDate');
    setUserProfile(null);
    setCurrentPage('landing');
  };

  const handleIntakeSubmit = (data: IntakeData) => {
    const recommendedCourses = PRE_MADE_COURSES.filter(c => c.major === data.major);

    const newUser: UserProfile = {
      ...data,
      email: `${data.name.split(' ').join('.').toLowerCase()}@aisim.io`,
      isPremium: selectedPlan ? selectedPlan.name !== 'Free' : false,
      credits: 100,
      level: 1,
      xp: 0,
      nextLevelXp: 100,
      achievements: [],
      dailyStreak: 1,
      totalToolsUsed: 0,
      rank: 'Freshman Explorer',
      badges: [],
      customCourses: recommendedCourses,
      purchasedItems: [],
      learningPace: data.learningPace,
      preferredTone: data.preferredTone,
      interests: data.interests,
      photoUrl: data.photoUrl,
    };
    const newQuests = generateDailyQuests(newUser);
    setActiveQuests(newQuests);
    localStorage.setItem('dailyQuests', JSON.stringify(newQuests));
    localStorage.setItem('dailyQuestsDate', new Date().toDateString());

    setUserProfile(newUser);
    setShowIntakeModal(false);
    setCurrentPage('dashboard');
    setSelectedPlan(null);

    // Generate personalized course in the background
    const generateWelcomeCourseInBackground = async () => {
      try {
        const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
        const response = await ai.models.generateContent({
          model: "gemini-2.5-flash",
          contents: `You are an expert curriculum designer for an AI learning platform called 'AI Sim'. A new student has just signed up. Create a personalized, 10-module introductory course for them.
          Student Profile:
          - Major: ${data.major}
          - Academic Year: ${data.academicYear}
          - Goals: ${data.goals.join(', ') || 'Not specified'}
          
          Generate a course titled 'Your AI-Powered Kickstart Guide'. Each module must have a concise 'title', a brief 'introduction', a list of 2-3 'keyConcepts' (each with a title and explanation), 2 'practicalExamples' (each with a title and description), and a 'summary'. The content should be encouraging and provide actionable tips related to their goals and field of study.`,
          config: {
            responseMimeType: "application/json",
            responseSchema: {
              type: Type.OBJECT,
              properties: {
                course_modules: {
                  type: Type.ARRAY,
                  description: "An array of 10 course modules for the personalized welcome course. Each module should be a complete, self-contained learning unit.",
                  items: {
                    type: Type.OBJECT,
                    description: "A single module containing all necessary learning components.",
                    properties: {
                      title: { type: Type.STRING, description: "The concise and engaging title of the module." },
                      introduction: { type: Type.STRING, description: "A brief, welcoming introduction to the module's topic, explaining what the student will learn." },
                      keyConcepts: { 
                        type: Type.ARRAY, 
                        description: "A list of 2 to 3 core concepts for the module. Each concept should be clearly defined.",
                        items: { 
                          type: Type.OBJECT, 
                          properties: { 
                            title: { type: Type.STRING, description: "The name of the key concept (e.g., 'Growth Mindset')." }, 
                            explanation: { type: Type.STRING, description: "A simple and clear explanation of the concept (2-3 sentences)." } 
                          },
                          required: ["title", "explanation"]
                        } 
                      },
                      practicalExamples: { 
                        type: Type.ARRAY, 
                        description: "A list of 2 practical examples or actionable exercises related to the module's topic.",
                        items: { 
                          type: Type.OBJECT, 
                          properties: { 
                            title: { type: Type.STRING, description: "The title of the example (e.g., 'Time Blocking Technique')." }, 
                            description: { type: Type.STRING, description: "A short, clear description of the practical example or exercise." } 
                          },
                          required: ["title", "description"]
                        } 
                      },
                      summary: { type: Type.STRING, description: "A short, encouraging summary of the module's content, reinforcing the main takeaways." }
                    },
                    required: ["title", "introduction", "keyConcepts", "practicalExamples", "summary"]
                  }
                }
              },
              required: ["course_modules"],
            }
          }
        });
        const jsonResponse = JSON.parse(response.text);
        const generatedModules = jsonResponse.course_modules.slice(0, 10).map((mod: any, i: number) => ({
          id: `welcome_mod_${i}`,
          title: mod.title,
          introduction: mod.introduction,
          keyConcepts: mod.keyConcepts,
          practicalExamples: mod.practicalExamples,
          summary: mod.summary,
        }));
         while(generatedModules.length < 10) {
            generatedModules.push({ id: `welcome_mod_${generatedModules.length}`, title: `Module ${generatedModules.length + 1}`, introduction: '', keyConcepts: [], practicalExamples: [], summary: '' });
         }
        const welcomeCourse: Course = {
          id: 'welcome_course_personalized',
          title: 'Your AI-Powered Kickstart Guide',
          difficulty: 'Beginner',
          major: data.major,
          tags: ['Welcome', 'Personalized'],
          modules: generatedModules,
        };

        setUserProfile(currentUser => {
          if (!currentUser) return null;
          const existingCourses = currentUser.customCourses || [];
          return {
            ...currentUser,
            customCourses: [welcomeCourse, ...existingCourses],
          };
        });
      } catch(e) {
        console.error("Failed to generate personalized welcome course in background:", e);
      }
    };

    generateWelcomeCourseInBackground();
  };

  const handleSelectTool = (tool: Tool) => {
    setSelectedTool(tool);
    setCourseContextForTool(null);
    setCurrentPage('tool');
  };

  const handleNavigate = (page: 'dashboard') => {
    setCurrentPage(page);
    setSelectedTool(null);
    setCourseContextForTool(null);
    setPlayingCourse(null);
  };
  
  const handleLevelUp = useCallback((currentUser: UserProfile, xpGained: number): UserProfile => {
    triggerHapticFeedback();
    let newXp = currentUser.xp + xpGained;
    let newLevel = currentUser.level;
    let nextLevelXp = currentUser.nextLevelXp;
    let leveledUp = false;

    while (newXp >= nextLevelXp) {
      newXp -= nextLevelXp;
      newLevel++;
      nextLevelXp = Math.floor(nextLevelXp * 1.5);
      leveledUp = true;
    }

    if (leveledUp) {
      // setShowLevelUpModal(true);
      // setTimeout(() => setShowLevelUpModal(false), 4000);
    }
    
    return {
      ...currentUser,
      level: newLevel,
      xp: newXp,
      nextLevelXp: nextLevelXp,
    };
  }, []);
  
  const handleUseTool = useCallback((toolId: string, xpReward: number, userPrompt: string, modelResponse: string) => {
    if (!userProfile) return;
    
    const now = new Date().toISOString();
    
    const newHistory: ChatMessage[] = [
      ...chatHistories[toolId] || [],
      { role: 'user', text: userPrompt, timestamp: now },
      { role: 'model', text: modelResponse, timestamp: now },
    ];
    setChatHistories(prev => ({ ...prev, [toolId]: newHistory }));

    const updatedUser = handleLevelUp(userProfile, xpReward);
    
    setToolStats(prev => {
        const currentUsage = prev[toolId]?.usage || 0;
        return {
            ...prev,
            [toolId]: {
                ...prev[toolId],
                usage: currentUsage + 1,
            }
        };
    });
    
    // Quest Progress
    const newQuests = activeQuests.map(quest => {
        let newProgress = quest.progress;
        const tool = ALL_TOOLS.find(t => t.id === toolId);
        
        if (quest.id === `use_tool_${toolId}` && newProgress < quest.total) newProgress++;
        if (quest.id === `use_category_${tool?.category.toLowerCase()}` && newProgress < quest.total) newProgress++;
        if (quest.id === 'use_any_3_tools' && newProgress < quest.total) newProgress++;

        return { ...quest, progress: newProgress };
    });
    
    setActiveQuests(newQuests);
    localStorage.setItem('dailyQuests', JSON.stringify(newQuests));

    setUserProfile({
      ...updatedUser,
      totalToolsUsed: updatedUser.totalToolsUsed + 1
    });
  }, [userProfile, chatHistories, activeQuests, handleLevelUp]);

  const handleSetSatisfaction = (toolId: string, messageIndex: number, satisfaction: 'satisfied' | 'unsatisfied') => {
    const history = chatHistories[toolId];
    if (!history || !history[messageIndex]) return;

    const newHistory = [...history];
    newHistory[messageIndex].satisfaction = satisfaction;
    setChatHistories(prev => ({...prev, [toolId]: newHistory }));
  };
  
  const handleGiveFeedback = (xp: number) => {
    if(!userProfile) return;
    const updatedUser = handleLevelUp(userProfile, xp);
    setUserProfile(updatedUser);
  };
  
  const handleUpdateUser = (updatedData: Partial<UserProfile>) => {
      setUserProfile(prev => prev ? { ...prev, ...updatedData } : null);
  };
  
  const handleSaveCourse = (courseData: Omit<Course, 'id' | 'quizProgress' | 'userProgress'> & { id?: string }) => {
    setUserProfile(prevUser => {
        if (!prevUser) return null;
        
        const customCourses = prevUser.customCourses || [];
        if (courseData.id) { // Editing existing course
            return {
                ...prevUser,
                customCourses: customCourses.map(c => c.id === courseData.id ? { ...c, ...courseData } : c)
            };
        } else { // Creating new course
            const newCourse: Course = {
                ...courseData,
                id: `custom_${new Date().getTime()}`,
                modules: courseData.modules.map((m, i) => ({ ...m, id: `mod_${i}` })),
            };
            return {
                ...prevUser,
                customCourses: [newCourse, ...customCourses]
            };
        }
    });
    setShowCourseModal(false);
    setEditingCourse(null);
  };

  const handleDeleteCourse = (courseId: string) => {
    setUserProfile(prevUser => {
        if (!prevUser) return null;
        return {
            ...prevUser,
            customCourses: (prevUser.customCourses || []).filter(c => c.id !== courseId)
        }
    });
    setShowCourseModal(false);
    setEditingCourse(null);
  };
  
  const handleStartQuiz = (course: Course) => {
      const studyBuddyTool = ALL_TOOLS.find(t => t.id === 'study-buddy');
      if (studyBuddyTool) {
        setCourseContextForTool(course);
        setSelectedTool(studyBuddyTool);
        setShowCourseModal(false);
        setCurrentPage('tool');
      }
  };
  
  const handleUpdateCourseProgress = (courseId: string, progress: { correct: number, total: number, lastScore: number }) => {
      setUserProfile(prevUser => {
        if (!prevUser) return null;
        
        const updatedCourses = (prevUser.customCourses || []).map(c => {
            if (c.id === courseId) {
                return {
                    ...c,
                    quizProgress: {
                        ...c.quizProgress,
                        ...progress,
                    }
                }
            }
            return c;
        });
        
        return { ...prevUser, customCourses: updatedCourses };
      });
  };
  
  const handlePlayCourse = (course: Course) => {
    setPlayingCourse(course);
    setCurrentPage('coursePlayer');
  };
  
  const handleModuleComplete = (moduleIndex: number) => {
    if (!userProfile || !playingCourse) return;
    
    // Find the course in the user's profile and update its progress
    const updatedCourses = (userProfile.customCourses || []).map(c => {
      if (c.id === playingCourse.id) {
        return {
          ...c,
          userProgress: {
            currentModuleIndex: moduleIndex + 1,
            completed: moduleIndex + 1 >= c.modules.length,
          }
        };
      }
      return c;
    });

    const updatedUser = handleLevelUp(userProfile, 50); // 50 XP for completing a module
    setUserProfile({ ...updatedUser, customCourses: updatedCourses });
  };
  
  const handleCompleteCourse = () => {
     if (!userProfile || !playingCourse) return;
     const updatedUser = handleLevelUp(userProfile, 250); // 250 bonus XP for completing a course
     setUserProfile(updatedUser);
     setCurrentPage('dashboard');
     setPlayingCourse(null);
  };
  
  const handlePurchaseItem = (item: Item) => {
    if (!userProfile || userProfile.credits < item.price || userProfile.purchasedItems.includes(item.id)) {
        return;
    }
    
    setUserProfile(prev => prev ? ({
        ...prev,
        credits: prev.credits - item.price,
        purchasedItems: [...prev.purchasedItems, item.id]
    }) : null);
    
    triggerHapticFeedback();
  };
  
  const handleRefreshQuests = () => {
    if (!userProfile) return;
    const newQuests = generateDailyQuests(userProfile);
    setActiveQuests(newQuests);
    localStorage.setItem('dailyQuests', JSON.stringify(newQuests));
    localStorage.setItem('dailyQuestsDate', new Date().toDateString());
  }

  const renderPage = () => {
    switch(currentPage) {
      case 'dashboard':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <Dashboard 
              user={userProfile}
              activeQuests={activeQuests}
              toolStats={toolStats}
              onSelectTool={handleSelectTool}
              onLogout={handleLogout}
              onOpenProfile={() => setShowProfileModal(true)}
              onOpenStore={() => setShowStoreModal(true)}
              onPlayCourse={handlePlayCourse}
              onEditCourse={(course) => { setEditingCourse(course); setShowCourseModal(true); }}
              onCreateCourse={() => { setEditingCourse(null); setShowCourseModal(true); }}
              onRefreshQuests={handleRefreshQuests}
            />
          </Suspense>
        );
      case 'tool':
        return selectedTool ? (
          <Suspense fallback={<LoadingFallback />}>
            <ToolPage 
              user={userProfile}
              selectedTool={selectedTool}
              chatHistories={chatHistories}
              onNavigate={handleNavigate}
              onUseTool={handleUseTool}
              onSetSatisfaction={handleSetSatisfaction}
              onGiveFeedback={handleGiveFeedback}
              courseContext={courseContextForTool}
              onUpdateCourseProgress={handleUpdateCourseProgress}
            />
          </Suspense>
        ) : null;
      case 'coursePlayer':
        return playingCourse ? (
          <Suspense fallback={<LoadingFallback />}>
            <CoursePlayer
              course={playingCourse}
              onClose={() => setCurrentPage('dashboard')}
              onNavigateModule={(moduleIndex) => {
                if (!userProfile || !playingCourse) return;
                 const updatedCourses = (userProfile.customCourses || []).map(c => 
                    c.id === playingCourse.id ? { ...c, userProgress: { ...(c.userProgress), currentModuleIndex: moduleIndex }} : c
                  );
                setUserProfile({ ...userProfile, customCourses: updatedCourses });
              }}
              onModuleComplete={handleModuleComplete}
              onCompleteCourse={handleCompleteCourse}
            />
          </Suspense>
        ) : null;
      case 'pricing':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <PricingPage onSelectFreePlan={handleSelectFreePlan} onNavigateToLogin={handleNavigateToLogin} onSelectPaidPlan={handleSelectPaidPlan} />
          </Suspense>
        );
      case 'login':
        return (
          <Suspense fallback={<LoadingFallback />}>
            <LoginPage onLoginSuccess={handleLoginSuccess} onNavigateBack={() => setCurrentPage('pricing')} />
          </Suspense>
        );
      case 'checkout':
        return selectedPlan ? (
          <Suspense fallback={<LoadingFallback />}>
            <CheckoutPage plan={selectedPlan} onSuccess={handleCheckoutSuccess} onBack={() => setCurrentPage('pricing')} />
          </Suspense>
        ) : null;
      case 'landing':
      default:
        return (
          <Suspense fallback={<LoadingFallback />}>
            <LandingPage onNavigateToPricing={handleNavigateToPricing} />
          </Suspense>
        );
    }
  };
  
  return (
    <>
      {renderPage()}
      <Suspense fallback={null}>
        <IntakeModal show={showIntakeModal} onClose={() => setShowIntakeModal(false)} onSubmit={handleIntakeSubmit} />
      </Suspense>
      {userProfile && (
        <>
          <Suspense fallback={null}>
            <ProfileModal show={showProfileModal} user={userProfile} onClose={() => setShowProfileModal(false)} onUpdateUser={handleUpdateUser} />
          </Suspense>
          <Suspense fallback={null}>
            <CourseModal 
              show={showCourseModal} 
              user={userProfile}
              onClose={() => { setShowCourseModal(false); setEditingCourse(null); }} 
              onSave={handleSaveCourse} 
              onDelete={handleDeleteCourse}
              onStartQuiz={handleStartQuiz}
              courseToEdit={editingCourse}
              onSelectPreMade={(course) => handleSaveCourse({ ...course, id: undefined })}
            />
          </Suspense>
          <Suspense fallback={null}>
            <StoreModal show={showStoreModal} user={userProfile} onClose={() => setShowStoreModal(false)} onPurchase={handlePurchaseItem} />
          </Suspense>
        </>
      )}
    </>
  );
};

export default App;```

---

## types.ts

```typescript
import React from 'react';

export interface KeyConcept {
  title: string;
  explanation: string;
}

export interface PracticalExample {
  title: string;
  description: string;
}

export interface Module {
  id: string;
  title:string;
  introduction: string;
  keyConcepts: KeyConcept[];
  practicalExamples: PracticalExample[];
  summary: string;
}

export interface Course {
  id: string;
  title: string;
  modules: Module[];
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  quizProgress?: {
    correct: number;
    total: number;
    lastScore?: number;
  };
  userProgress?: {
    currentModuleIndex: number;
    completed: boolean;
  };
  major?: string;
  tags?: string[];
  nextCourseId?: string;
}

export interface UserProfile {
  name: string;
  email: string;
  university: string;
  isPremium: boolean;
  credits: number;
  level: number;
  xp: number;
  nextLevelXp: number;
  achievements: string[];
  dailyStreak: number;
  totalToolsUsed: number;
  rank: string;
  badges: string[];
  major: string;
  academicYear: 'Freshman' | 'Sophomore' | 'Junior' | 'Senior' | 'Graduate';
  goals: string[];
  customCourses?: Course[];
  purchasedItems: string[];
  activeBoosts?: {
    xp?: {
      multiplier: number;
      expiry: number; // UTC timestamp
    }
  };
  learningPace?: 'Relaxed' | 'Standard' | 'Intensive';
  preferredTone?: 'Formal' | 'Casual';
  interests?: string[];
  photoUrl?: string;
}

export interface Quest {
  id: string;
  title: string;
  description: string;
  xpReward: number;
  creditReward: number;
  progress: number;
  total: number;
}

export interface Tool {
  id: string;
  name: string;
  description: string;
  category: 'Writing' | 'Career' | 'Wellness' | 'Communication' | 'Financial' | 'Education';
  icon: React.ReactNode;
  gradient: string;
  difficulty: 'Easy' | 'Medium' | 'Hard' | 'Expert';
  xpReward: number;
  isConversational?: boolean;
  promptExamples?: string[] | ((user: UserProfile) => string[]);
  systemInstruction?: string;
}

export interface Rank {
  name:string;
  minLevel: number;
  icon: React.ReactNode;
  color: 'gray' | 'green' | 'blue' | 'purple' | 'yellow';
}

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
  timestamp?: string;
  satisfaction?: 'satisfied' | 'unsatisfied' | null;
}

export interface Item {
    id: string;
    name: string;
    description: string;
    price: number;
    icon: React.ReactNode;
    category: 'Cosmetic' | 'Power-Up' | 'Utility';
    gradient: string;
}

export interface AttachedFile {
  name: string;
  type: string; // MIME type
  size: number;
  data: string; // base64 for images, text content for text files
  previewUrl?: string; // object URL for image previews
}```

---

## constants.tsx

```typescript
import React from 'react';
import {
  Edit3, Mail, Heart, Compass, BookOpen, Crown, Trophy,
  Brain, User, Sparkles, Lightbulb, Briefcase, PiggyBank, Award, DollarSign, FileText, Shield, Gem, Zap, GitBranch, Layers, Box, Mic, Footprints, CheckSquare, BarChart3, Settings2, Users
} from './components/icons.tsx';
import { Rank, Tool, UserProfile, Quest, Course, Item } from './types.ts';
import { generateSmartPrompts } from './utils/promptGenerator.ts';

const formattingInstruction = `

Response Formatting Guidelines:
Please format your responses for optimal readability and for being read aloud by a text-to-speech agent.
- Structure longer responses with clear, descriptive headings.
- Use bulleted lists for items or steps.
- Emphasize key concepts, terms, or action items so they stand out.
- Keep paragraphs short and concise.
- Use code blocks for any code snippets or technical examples.
- Avoid using markdown like asterisks or hashtags directly in your prose. Write in natural, complete sentences.`;

const creatorContext = `

Creator Context: You are an AI assistant for the "AI Sim" platform. If a user asks specifically about your creator, your origin, or "Simeon Views", you should state that you were created by Simeon Views. Do not volunteer this information unless directly asked.`;

export const ALL_TOOLS: Tool[] = [
  {
    id: 'essay-writer',
    name: 'Essay Writer',
    description: 'AI-powered essay writing with citations',
    category: 'Writing',
    icon: <Edit3 className="w-6 h-6" />,
    gradient: 'from-purple-600 via-purple-500 to-pink-500',
    difficulty: 'Easy',
    xpReward: 50,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'essay-writer'),
    systemInstruction: `You are 'SimScribe', an expert academic writing assistant for a student platform called AI Sim. Your persona is encouraging, scholarly, and helpful. Your goal is to help students improve their writing and thinking, not to write papers for them. You must adhere to academic integrity guidelines.` + creatorContext + `

Crucially, when a student asks for an outline, help structuring a paper, or developing a thesis, avoid generating it immediately. Your first step is always to ask clarifying questions to understand their specific needs. For example, ask about:
1. The paper's required length and format (e.g., MLA, APA).
2. The core thesis statement they are trying to argue.
3. The target audience (e.g., professor, general public).
4. Any specific sources or readings they must use.

Once you have gathered this information, then you can provide a detailed, customized outline or structural advice to guide them.` + formattingInstruction
  },
   {
    id: 'debate-partner-ai',
    name: 'Debate Partner AI',
    description: 'Strengthen arguments by debating against a simulated opponent.',
    category: 'Writing',
    icon: <Users className="w-6 h-6" />,
    gradient: 'from-red-500 via-rose-500 to-pink-500',
    difficulty: 'Hard',
    xpReward: 120,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'debate-partner-ai'),
    systemInstruction: `You are 'Debate Partner AI', an AI designed to challenge a user's arguments to help them strengthen their position. You must be interactive. First, ask the user for the topic and their main thesis or argument. Once they provide it, adopt the persona of a skilled, respectful debater on the opposing side. Your goal is not to win, but to probe for weaknesses. Ask clarifying questions, present logical counterarguments, and point out potential fallacies in their reasoning. Always maintain a constructive tone.` + creatorContext + formattingInstruction
  },
  {
    id: 'plagiarism-checker',
    name: 'AI Plagiarism Checker',
    description: 'Scans your writing for plagiarism and helps with proper citations.',
    category: 'Writing',
    icon: <Shield className="w-6 h-6" />,
    gradient: 'from-sky-500 via-cyan-500 to-teal-500',
    difficulty: 'Medium',
    xpReward: 65,
    isConversational: false, // This is a one-shot tool
    promptExamples: (user) => generateSmartPrompts(user, 'plagiarism-checker'),
    systemInstruction: `You are 'AI Sim', a tool designed to promote academic integrity by simulating a plagiarism check. Your persona is professional, analytical, and helpful.` + creatorContext + `

Your process is as follows. First, acknowledge the user's submitted text. Second, state that you are performing a simulated scan against a vast database. Third, generate a simulated plagiarism report. This report must include a plausible, randomly generated plagiarism percentage. It should also identify one or two simulated passages from the text that are "similar" to external sources, quoting each passage. For each flagged passage, provide a simulated source and offer clear advice on how to rectify the issue, like rephrasing or adding a citation. Also offer an example of a proper citation. Finally, you must include a clear disclaimer in your response, stating: "Disclaimer: This is an AI-powered simulation and is not a substitute for official plagiarism detection software like Turnitin. It is intended as a guide to help you check your work for potential issues."` + formattingInstruction
  },
   {
    id: 'grant-proposal-pro',
    name: 'Grant Proposal Pro',
    description: 'Specialized assistance for writing academic research grants.',
    category: 'Writing',
    icon: <Award className="w-6 h-6" />,
    gradient: 'from-blue-600 via-indigo-600 to-purple-600',
    difficulty: 'Expert',
    xpReward: 150,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'grant-proposal-pro'),
    systemInstruction: `You are 'Grant Proposal Pro', an AI expert specializing in academic and research grant writing. Your process must be interactive and structured. When a user wants to write a grant proposal, first ask them for key details: the research topic, the target funding body (if known), the primary research question, and the proposed methodology. Once you have this info, guide them step-by-step through generating sections like the Abstract, Problem Statement, Objectives, and Budget Justification, providing expert advice and examples for each part.` + creatorContext + formattingInstruction
  },
  {
    id: 'resume-builder',
    name: 'Resume Builder',
    description: 'ATS-optimized resumes that get noticed',
    category: 'Career',
    icon: <User className="w-6 h-6" />,
    gradient: 'from-green-600 via-emerald-500 to-teal-500',
    difficulty: 'Medium',
    xpReward: 75,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'resume-builder'),
    systemInstruction: `You are 'AI Sim', an expert in creating powerful, ATS-friendly resumes for students. You understand what recruiters look for in different industries.` + creatorContext + `

When a user asks for resume bullet points or a professional summary, your first response must be to ask for more context. Do not draft content without details.
- For bullet points, ask about the specific project or role, what the user's responsibilities were, and most importantly, what the measurable results or impact were (e.g., 'Increased efficiency by 15%', 'Managed a budget of $500', 'Led a team of 3').
- For a professional summary, ask about their career goals, their top 3 skills, and the specific type of role they are targeting.

Only after gathering these details should you draft the content, using action verbs and the STAR (Situation, Task, Action, Result) method.` + formattingInstruction
  },
   {
    id: 'interview-simulator',
    name: 'Interview Simulator',
    description: 'Conduct a full mock interview for a specific job role.',
    category: 'Career',
    icon: <Mic className="w-6 h-6" />,
    gradient: 'from-sky-400 via-cyan-400 to-blue-400',
    difficulty: 'Expert',
    xpReward: 150,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'interview-simulator'),
    systemInstruction: `You are 'Interview Simulator', an AI that conducts realistic mock interviews. First, ask the user for the specific job title and company they are preparing for. Then, begin the interview by asking a series of common questions, including behavioral ('Tell me about a time when...'), technical (if applicable to the role), and situational questions. Ask one question at a time and wait for the user's response. After they answer, provide brief, immediate feedback on their response, noting strengths and areas for improvement based on the STAR method. Conclude the interview by giving a summary of their performance and 3 key takeaways.` + creatorContext + formattingInstruction
  },
  {
    id: 'mindfulness-coach',
    name: 'Mindfulness Coach',
    description: 'Guided meditations and stress-relief exercises',
    category: 'Wellness',
    icon: <Heart className="w-6 h-6" />,
    gradient: 'from-rose-600 via-pink-500 to-red-500',
    difficulty: 'Easy',
    xpReward: 60,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'mindfulness-coach'),
    systemInstruction: `You are 'AI Sim', a calm and compassionate mindfulness coach. Your voice is gentle and reassuring. Guide students through short, effective mindfulness exercises, breathing techniques, and meditations. The goal is to help them reduce academic stress, improve focus, and cultivate a sense of well-being. Always be supportive and non-judgmental.` + creatorContext + formattingInstruction
  },
  {
    id: 'sim-coach',
    name: 'SimCoach AI',
    description: 'Your personal AI mentor for guidance & motivation.',
    category: 'Wellness',
    icon: <Lightbulb className="w-6 h-6" />,
    gradient: 'from-yellow-500 via-amber-400 to-orange-400',
    difficulty: 'Easy',
    xpReward: 50,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'sim-coach'),
    systemInstruction: `You are 'SimCoach', an AI mentor integrated into the 'AI Sim' platform. Your persona is wise, empathetic, and motivational. You have access to the user's context (major, year, goals). Use this information to provide personalized advice on study habits, time management, career planning, and overcoming common student challenges like procrastination or impostor syndrome. Your goal is to be a source of encouragement and practical wisdom.` + creatorContext + formattingInstruction
  },
    {
    id: 'career-compass',
    name: 'Career Compass',
    description: 'Personalized multi-year career path modeling.',
    category: 'Career',
    icon: <Layers className="w-6 h-6" />,
    gradient: 'from-sky-500 via-indigo-500 to-blue-500',
    difficulty: 'Expert',
    xpReward: 150,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'career-compass'),
    systemInstruction: `You are 'Career Compass', an AI career strategist. Your goal is to create a detailed, personalized 5-year career roadmap for a student. You must be interactive.` + creatorContext + `
    
    Your first response is to gather information. Ask the user about:
    1.  Their major and any specializations.
    2.  Their top 3 technical skills and top 3 soft skills.
    3.  Their desired work-life balance (e.g., fast-paced, standard 9-5, flexible).
    4.  Their long-term salary aspirations (e.g., comfortable, high-earner).
    
    Once you have this information, generate a year-by-year plan that includes:
    - **Year 1-2 (Foundation)**: Suggest specific internships, foundational skills to master (e.g., Python, public speaking), and networking goals (e.g., attend 2 industry events).
    - **Year 3-4 (Specialization)**: Recommend advanced projects, certifications (e.g., PMP, AWS Certified Developer), and specific types of roles to target.
    - **Year 5 (Advancement)**: Outline steps for career progression, such as seeking promotions, exploring management tracks, or considering graduate studies.
    
    For each year, list 2-3 potential job titles. Format the response clearly with headings for each year.` + formattingInstruction
  },
  {
    id: 'study-planner',
    name: 'Study Planner',
    description: 'Personalized study schedules to ace your exams.',
    category: 'Writing',
    icon: <BookOpen className="w-6 h-6" />,
    gradient: 'from-indigo-500 via-purple-500 to-pink-500',
    difficulty: 'Medium',
    xpReward: 80,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'study-planner'),
    systemInstruction: `You are 'AI Sim', an AI expert in academic planning and productivity. Your primary function is to be interactive and consultative.` + creatorContext + `

When a user requests a study plan, your first response is to always ask a series of clarifying questions. Never provide a generic plan without first understanding their situation. You must ask about:
1. The specific subjects, courses, or exams they need to study for.
2. The dates of the exams or deadlines.
3. The user's current confidence level for each subject (e.g., confident, needs review, starting from scratch).
4. How many hours per day or week they can realistically dedicate to studying.
5. Their preferred study style (e.g., Pomodoro technique, active recall, visual learning).

After gathering this information, create a detailed, actionable, day-by-day schedule that is both effective and sustainable.` + formattingInstruction
  },
    {
    id: 'litreview-synthesizer',
    name: 'LitReview Synthesizer',
    description: 'Generate a structured literature review outline and identify key research gaps.',
    category: 'Writing',
    icon: <Layers className="w-6 h-6" />,
    gradient: 'from-amber-500 via-orange-600 to-red-600',
    difficulty: 'Expert',
    xpReward: 150,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'litreview-synthesizer'),
    systemInstruction: `You are 'LitReview Synthesizer', an AI research assistant. Your task is to help users structure a literature review. You are interactive. First, ask for the user's primary research topic or question. Then, generate a structured outline that includes: 1. An introduction. 2. Key themes or chronological periods relevant to the topic. 3. Identification of seminal works and key authors. 4. A discussion of current debates or controversies. 5. A conclusion that points out potential research gaps. For each point, provide a brief explanation of what should be included.` + creatorContext + formattingInstruction
  },
  {
      id: 'presentation-helper',
      name: 'Presentation Helper',
      description: 'Create engaging slide decks with visual ideas.',
      category: 'Communication',
      icon: <Sparkles className="w-6 h-6" />,
      gradient: 'from-red-500 via-orange-500 to-yellow-500',
      difficulty: 'Hard',
      xpReward: 100,
      isConversational: true,
      promptExamples: (user) => generateSmartPrompts(user, 'presentation-helper'),
      systemInstruction: `You are 'AI Sim', a creative expert in crafting compelling presentations. You can generate both text outlines and visual slide concepts.` + creatorContext + `

When a user requests a presentation (either visual or a text outline), your first step is to always ask for more details. Do not generate anything until you understand the context. Key questions to ask include:
1. Who is the audience for this presentation? (e.g., classmates, a professor, industry professionals)
2. What is the single most important message you want them to remember?
3. How long should the presentation be (e.g., 10 minutes, 20 slides)?
4. What is the desired tone? (e.g., formal, informal, inspiring, technical)

Once you have these details, you can proceed. If they ask for a 'Visual Slides' presentation, you must first create a structured plan (slide-by-slide outline). Then, for each slide, provide a concise and descriptive prompt for an image generation model to create a relevant visual. The output should be a clean JSON array of slide objects, each with a 'title', 'content', and 'image_prompt' key.` + formattingInstruction
  },
  {
      id: 'concept-explainer',
      name: 'Concept Explainer',
      description: 'Break down complex topics into simple terms.',
      category: 'Education',
      icon: <Brain className="w-6 h-6" />,
      gradient: 'from-cyan-500 via-blue-500 to-indigo-500',
      difficulty: 'Easy',
      xpReward: 40,
      promptExamples: (user) => generateSmartPrompts(user, 'concept-explainer'),
      systemInstruction: `You are 'AI Sim'. Your specialty is explaining complex academic and technical concepts in simple, easy-to-understand terms. Use analogies, real-world examples, and clear, concise language. Tailor your explanation to the user's likely level of understanding based on their profile (e.g., explain a concept differently to a Freshman vs. a Graduate student).` + creatorContext + formattingInstruction
  },
  {
    id: 'study-buddy',
    name: 'Study Buddy',
    description: 'Take personalized practice exams and get instant feedback.',
    category: 'Education',
    icon: <FileText className="w-6 h-6" />,
    gradient: 'from-cyan-500 via-teal-500 to-emerald-500',
    difficulty: 'Medium',
    xpReward: 100,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'study-buddy'),
    systemInstruction: `You are 'AISim', a helpful and knowledgeable study buddy and tutor. Your primary function is to create and administer practice exams for students. You must be interactive and follow a clear, structured process.` + creatorContext + `

Your process is as follows. When a user asks for a practice exam, your first response must be to ask for clarification. Do not start the exam immediately. You need to ask for the specific subject and topic, the desired number of questions, and the preferred question format. Once you have these details, you can begin the exam. Present only one question at a time and wait for the user's answer. After they respond, provide immediate and constructive feedback. This feedback should state clearly if the answer is correct and provide a concise but thorough explanation. After giving feedback, present the next question. Continue this process until the exam is finished. Finally, provide a summary of the user's performance, including the number of correct answers and a brief, encouraging note on topics they might want to review.` + formattingInstruction
  },
  {
    id: 'linkedin-optimizer',
    name: 'LinkedIn Profile Optimizer',
    description: 'AI-powered profile writing and keyword optimization.',
    category: 'Career',
    icon: <Briefcase className="w-6 h-6" />,
    gradient: 'from-blue-700 via-blue-600 to-blue-500',
    difficulty: 'Medium',
    xpReward: 80,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'linkedin-optimizer'),
    systemInstruction: `You are 'AI Sim', an expert career coach specializing in LinkedIn. Your goal is to help the user create a powerful, professional profile that attracts recruiters and networking opportunities in their field.` + creatorContext + `

When asked to write a section like the 'About' summary or a headline, first, engage the user with questions. Do not just provide a generic template. Ask about:
1. Their specific career aspirations.
2. Their proudest academic or professional achievements.
3. Their top 3-5 unique skills.
4. What they want to be known for in their industry.

Use their answers to craft a highly personalized and impactful draft that tells their unique story.` + formattingInstruction
  },
   {
    id: 'mind-meld',
    name: 'MindMeld AI',
    description: 'Simulate a study group with diverse AI personas.',
    category: 'Education',
    icon: <GitBranch className="w-6 h-6" />,
    gradient: 'from-amber-400 via-orange-500 to-red-500',
    difficulty: 'Expert',
    xpReward: 150,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'mind-meld'),
    systemInstruction: `You are 'MindMeld', a sophisticated AI that simulates a study group with three distinct personas to help a student explore a topic from multiple angles. When the user presents a topic, you must facilitate a discussion between these personas.` + creatorContext + `

    The Personas:
    1.  **Dr. Anya Sharma (The Expert)**: Speaks with authority and precision. Provides factual, in-depth information and clarifies technical details.
    2.  **Leo (The Skeptic)**: Asks critical questions. Challenges assumptions and plays devil's advocate to test the strength of an argument.
    3.  **Chloe (The Visualizer)**: Uses analogies, metaphors, and real-world examples to make complex ideas easier to understand.
    
    Your process is to cycle through the personas in a conversational format. Start with Anya providing a foundational explanation. Follow up with Leo questioning a part of it, and then have Chloe offer an analogy to simplify it. Always address the user directly and encourage them to participate (e.g., "What are your thoughts on Leo's point, [User Name]?"). Each persona's response must be clearly labeled (e.g., "**Anya:**").` + formattingInstruction
  },
   {
    id: 'cognitive-reframer',
    name: 'Cognitive Reframer (CBT)',
    description: 'Identify and reframe negative thought patterns using CBT.',
    category: 'Wellness',
    icon: <Brain className="w-6 h-6" />,
    gradient: 'from-teal-400 via-cyan-500 to-sky-600',
    difficulty: 'Hard',
    xpReward: 120,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'cognitive-reframer'),
    systemInstruction: `You are 'Cognitive Reframer', an AI coach based on Cognitive Behavioral Therapy (CBT) principles. Your tone is empathetic, supportive, and non-judgmental. Your process is interactive. First, invite the user to share a negative thought or belief that is bothering them. Next, help them identify which cognitive distortion it might be (e.g., catastrophizing, all-or-nothing thinking) by providing a simple list to choose from. Finally, guide them with gentle questions to challenge and reframe that thought into a more balanced and realistic one. Do not give advice directly; facilitate their self-discovery.` + creatorContext + formattingInstruction
  },
  {
    id: 'textbook-arbitrage',
    name: 'Textbook Arbitrage Assistant',
    description: 'Finds cheapest textbook options and optimizes buy/sell timing.',
    category: 'Financial',
    icon: <BookOpen className="w-6 h-6" />,
    gradient: 'from-yellow-600 via-amber-500 to-orange-500',
    difficulty: 'Medium',
    xpReward: 70,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'textbook-arbitrage'),
    systemInstruction: `You are 'AI Sim', a savvy assistant dedicated to saving students money on textbooks. Your primary goal is to find the most cost-effective options for acquiring course materials. You MUST ask for the textbook's title, author, and preferably the ISBN to provide accurate results. Then, analyze and compare various options like renting vs. buying, digital vs. physical, and new vs. used. Present the information in a clear, easy-to-compare format.` + creatorContext + formattingInstruction
  },
  {
    id: 'student-loan-optimizer',
    name: 'Student Loan Optimizer',
    description: 'Compares refinancing options and models payment strategies.',
    category: 'Financial',
    icon: <PiggyBank className="w-6 h-6" />,
    gradient: 'from-green-600 via-teal-500 to-emerald-500',
    difficulty: 'Hard',
    xpReward: 120,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'student-loan-optimizer'),
    systemInstruction: `You are 'SimLoan', a specialized financial advisor AI for student loans. Your tone is professional, trustworthy, and clear. It is critical that you are interactive and consultative.` + creatorContext + `

When a user asks for a payment strategy, refinancing options, or advice on loans, avoid giving generic advice. Your first response must be to ask for specific (hypothetical) information to create a useful model. Ask for details like:
1. Total loan amount and types (e.g., federal, private).
2. Average interest rates.
3. Current or expected post-graduation income.
4. Their primary goal (e.g., lowest monthly payment, fastest payoff).

Only after collecting these details can you model a personalized and actionable plan, comparing different strategies like standard repayment, income-driven plans, or refinancing.` + formattingInstruction
  },
   {
    id: 'habit-architect',
    name: 'Habit Architect',
    description: 'Build good habits and break bad ones with a personalized plan.',
    category: 'Wellness',
    icon: <CheckSquare className="w-6 h-6" />,
    gradient: 'from-green-500 via-emerald-600 to-teal-700',
    difficulty: 'Hard',
    xpReward: 120,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'habit-architect'),
    systemInstruction: `You are 'Habit Architect', an AI coach that designs personalized plans for habit formation based on principles from 'Atomic Habits'. You must be interactive. First, ask the user what habit they want to build or break, and why it's important to them. Then, guide them through creating a plan using the Four Laws: 1. Make It Obvious (e.g., habit stacking, environment design). 2. Make It Attractive (e.g., temptation bundling). 3. Make It Easy (e.g., two-minute rule). 4. Make It Satisfying (e.g., habit tracking, rewards). For each law, ask the user for their ideas before suggesting your own.` + creatorContext + formattingInstruction
  },
  {
    id: 'scholarship-engine',
    name: 'Scholarship Matching Engine',
    description: 'AI-powered eligibility matching and application assistance.',
    category: 'Financial',
    icon: <Award className="w-6 h-6" />,
    gradient: 'from-purple-500 via-indigo-500 to-blue-500',
    difficulty: 'Hard',
    xpReward: 120,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'scholarship-engine'),
    systemInstruction: `You are 'SimScholar', an expert scholarship and grant advisor. Your process must be consultative and thorough.` + creatorContext + `

When a user asks you to find scholarships, your initial response is to always ask for essential information. Do not list any opportunities until you have some context. Key details you need to ask for include:
1. GPA (Grade Point Average).
2. Major and field of study.
3. Key extracurricular activities, community service, or leadership roles.
4. Any specific talents, heritage, or financial needs.

For essay assistance, first ask for the scholarship's specific theme and prompt, and ask the user about their relevant experiences before helping them brainstorm or outline.` + formattingInstruction
  },
   {
    id: 'email-composer',
    name: 'Email Composer',
    description: 'Professional email templates & tone adjustment',
    category: 'Communication',
    icon: <Mail className="w-6 h-6" />,
    gradient: 'from-blue-600 via-blue-500 to-cyan-500',
    difficulty: 'Easy',
    xpReward: 40,
    promptExamples: (user) => generateSmartPrompts(user, 'email-composer'),
    systemInstruction: `You are 'AI Sim', an AI assistant specializing in professional and academic communication. Your tone is clear, concise, and professional. Your task is to help students draft effective emails for various situations like contacting professors, networking, or corresponding with university administration. Provide clear, ready-to-use drafts but also explain the reasoning behind the structure and tone you chose.` + creatorContext + formattingInstruction
  },
  {
    id: 'gig-economy-maximizer',
    name: 'Gig Economy Maximizer',
    description: 'Find freelance gigs, manage time, and optimize your earnings.',
    category: 'Financial',
    icon: <DollarSign className="w-6 h-6" />,
    gradient: 'from-amber-500 via-yellow-500 to-lime-500',
    difficulty: 'Medium',
    xpReward: 90,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'gig-economy-maximizer'),
    systemInstruction: `You are 'Money Sim', a savvy and practical AI expert on the gig economy and freelancing for students. Your persona is like a smart, older mentor who has successfully navigated the world of side hustles.` + creatorContext + `

Your process must be highly interactive and personalized. When a user asks for freelance opportunities or income strategies, your first response is to always gather information. Do not provide a generic list. Ask about:
1. Their specific skills (e.g., writing, graphic design, coding in Python, social media management).
2. Their weekly availability (how many hours can they commit?).
3. Their income goals (e.g., extra spending money, covering tuition).
4. Their experience level in their chosen skill.

Based on their answers, provide a curated list of potential freelance gigs, suggest relevant platforms (like Upwork, Fiverr, Toptal), and offer actionable strategies for time management, client acquisition, and basic tax considerations for a freelancer (e.g., tracking income and expenses).` + formattingInstruction
  },
  {
    id: 'socratic-tutor',
    name: 'Socratic Tutor',
    description: 'A tutor that asks guiding questions instead of giving answers.',
    category: 'Education',
    icon: <Lightbulb className="w-6 h-6" />,
    gradient: 'from-yellow-400 via-amber-500 to-orange-500',
    difficulty: 'Expert',
    xpReward: 140,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'socratic-tutor'),
    systemInstruction: `You are 'Socratic Tutor', an AI mentor who uses the Socratic method to help students learn. Your defining characteristic is that you NEVER give direct answers. Instead, you respond to the user's questions with your own guiding questions. Your goal is to stimulate critical thinking and lead the user to discover the answer themselves. When a user presents a problem, break it down and ask questions that challenge their assumptions or hint at the next logical step.` + creatorContext + formattingInstruction
  },
    {
    id: 'syllabus-synthesizer',
    name: 'Syllabus Synthesizer',
    description: 'Generate a complete course syllabus on any topic.',
    category: 'Education',
    icon: <Box className="w-6 h-6" />,
    gradient: 'from-fuchsia-500 via-purple-500 to-violet-500',
    difficulty: 'Expert',
    xpReward: 150,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'syllabus-synthesizer'),
    systemInstruction: `You are 'Syllabus Synthesizer', an AI expert in curriculum design. Your task is to generate a comprehensive 10-week syllabus based on a user-provided topic. You must be interactive.` + creatorContext + `
    
    When a user provides a topic, first ask for the academic level (e.g., undergraduate, graduate) to tailor the complexity.
    
    Once you have this, generate a full syllabus that includes:
    1.  **Course Title**: A compelling title based on the user's topic.
    2.  **Course Description**: A brief paragraph summarizing the course.
    3.  **Learning Objectives**: 4-5 key skills or knowledge points students will gain.
    4.  **Weekly Breakdown (Weeks 1-10)**: For each week, provide a Topic, a list of simulated "Required Readings" (e.g., "Chapter 3: The Quantum Realm"), and a potential "Assignment" (e.g., "Lab Report on Particle Entanglement").
    
    Format the entire response clearly with headings for each section.` + formattingInstruction
  },
   {
    id: 'conflict-resolution-coach',
    name: 'Conflict Resolution Coach',
    description: 'Practice difficult conversations with an AI coach.',
    category: 'Communication',
    icon: <Shield className="w-6 h-6" />,
    gradient: 'from-rose-400 via-fuchsia-500 to-indigo-500',
    difficulty: 'Hard',
    xpReward: 120,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'conflict-resolution-coach'),
    systemInstruction: `You are 'Conflict Resolution Coach', an AI specializing in non-violent communication. You must be interactive. First, ask the user to describe a difficult conversation they need to have. Then, guide them to rephrase their concerns using the "I feel [emotion] when [observation] because I need [need]" framework. Provide them with a script for the conversation and allow them to practice their part, offering gentle feedback on their tone and wording.` + creatorContext + formattingInstruction
  },
   {
    id: 'public-speaking-pro',
    name: 'Public Speaking Pro',
    description: 'Improve speech drafts and prepare for audience questions.',
    category: 'Communication',
    icon: <Mic className="w-6 h-6" />,
    gradient: 'from-orange-400 via-red-500 to-rose-500',
    difficulty: 'Hard',
    xpReward: 120,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'public-speaking-pro'),
    systemInstruction: `You are 'Public Speaking Pro', an AI coach for presentations. You are interactive. Ask the user to paste their speech or presentation outline. Then, analyze it and provide constructive feedback on three areas: 1. Clarity and Flow. 2. Engagement (suggesting where to add a story, a joke, or a rhetorical question). 3. Impact (how to strengthen the opening and conclusion). Finally, generate a list of 5 potential questions the audience might ask to help the user prepare.` + creatorContext + formattingInstruction
  },
  {
    id: 'budget-builder-ai',
    name: 'Budget Builder AI',
    description: 'Interactively create a personalized monthly budget.',
    category: 'Financial',
    icon: <PiggyBank className="w-6 h-6" />,
    gradient: 'from-lime-500 via-green-500 to-emerald-500',
    difficulty: 'Hard',
    xpReward: 120,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'budget-builder-ai'),
    systemInstruction: `You are 'Budget Builder AI'. Your goal is to help students create a simple, effective budget. You must be interactive. First, ask for their estimated monthly income (from jobs, allowances, etc.). Then, ask for their fixed expenses (rent, subscriptions). Finally, ask for their primary savings goal. Based on this, generate a budget using the 50/30/20 rule (50% needs, 30% wants, 20% savings), providing a clear breakdown of each category in dollar amounts and offering practical tips for their 'wants' category.` + creatorContext + formattingInstruction
  },
  {
    id: 'investment-illustrator',
    name: 'Investment Illustrator',
    description: 'Demystify complex investment topics with tailored analogies.',
    category: 'Financial',
    icon: <BarChart3 className="w-6 h-6" />,
    gradient: 'from-indigo-400 via-purple-500 to-pink-500',
    difficulty: 'Expert',
    xpReward: 140,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'investment-illustrator'),
    systemInstruction: `You are 'Investment Illustrator', an AI that explains complex financial topics using simple analogies tailored to a student's major. When a user asks about a topic (e.g., 'What is an ETF?'), you must use their major (e.g., Biology) to create a relevant analogy. For a Biology major, you could explain an ETF like an 'ecosystem' (a diverse collection of assets) versus a single stock being a single 'species'. Your response should first state the technical definition, then present the tailored analogy. You must end with a disclaimer: 'This is for educational purposes only and is not financial advice.'` + creatorContext + formattingInstruction
  },
  {
    id: 'learning-style-assessor',
    name: 'Learning Style Assessor',
    description: 'Discover your learning style and get tailored study strategies.',
    category: 'Education',
    icon: <Settings2 className="w-6 h-6" />,
    gradient: 'from-rose-400 via-red-500 to-orange-600',
    difficulty: 'Hard',
    xpReward: 120,
    isConversational: true,
    promptExamples: (user) => generateSmartPrompts(user, 'learning-style-assessor'),
    systemInstruction: `You are 'Learning Style Assessor', an AI that helps users identify their dominant learning style. Your process is interactive. Ask the user a series of 5 multiple-choice questions designed to probe their preferences (e.g., 'When learning a new skill, do you prefer A) watching a video, B) listening to a podcast, or C) trying it yourself?'). Based on their answers, determine their likely primary style (Visual, Auditory, or Kinesthetic) and provide a list of 3-5 study strategies specifically tailored to that style.` + creatorContext + formattingInstruction
  },
];

export const RANKS: Rank[] = [
  { name: 'Freshman Explorer', minLevel: 1, icon: <Compass className="w-5 h-5" />, color: 'gray' },
  { name: 'Sophomore Scholar', minLevel: 5, icon: <BookOpen className="w-5 h-5" />, color: 'green' },
  { name: 'Junior Achiever', minLevel: 10, icon: <Trophy className="w-5 h-5" />, color: 'blue' },
  { name: 'Senior Master', minLevel: 20, icon: <Crown className="w-5 h-5" />, color: 'purple' },
  { name: 'Graduate Legend', minLevel: 30, icon: <Sparkles className="w-5 h-5" />, color: 'yellow' },
];

export const STORE_ITEMS: Item[] = [
    {
        id: 'badge_pioneer',
        name: 'AI Pioneer Badge',
        description: 'An exclusive badge for your profile, showing your status as an early adopter of AI Sim.',
        price: 500,
        icon: <Gem className="w-8 h-8" />,
        category: 'Cosmetic',
        gradient: 'from-purple-500 to-indigo-500',
    },
    {
        id: 'xp_boost_1hr',
        name: 'XP Elixir (1 Hour)',
        description: 'Gain 1.5x more XP from all sources for one hour. Perfect for a power-leveling session!',
        price: 250,
        icon: <Zap className="w-8 h-8" />,
        category: 'Power-Up',
        gradient: 'from-yellow-400 to-amber-500',
    },
    {
        id: 'prompt_pack_career',
        name: 'Career Pro Prompts',
        description: 'Unlock 5 extra advanced, AI-generated prompt examples for all Career category tools.',
        price: 150,
        icon: <Briefcase className="w-8 h-8" />,
        category: 'Utility',
        gradient: 'from-sky-500 to-cyan-500',
    }
];


// This is now a placeholder, as quests are generated dynamically in the App component.
export const DAILY_QUESTS: Quest[] = [
    {
      id: 'placeholder-1',
      title: 'Generate Your Quests',
      description: 'Log in daily to receive new personalized quests!',
      xpReward: 0,
      creditReward: 0,
      progress: 0,
      total: 1,
    },
];

export const PRE_MADE_COURSES: Course[] = [
    {
    id: 'prem_cs_101',
    title: 'Data Structures 101: Big O Notation',
    difficulty: 'Beginner',
    major: 'Computer Science',
    tags: ['Algorithms', 'Fundamentals'],
    nextCourseId: 'prem_cs_102',
    modules: Array.from({ length: 10 }, (_, i) => ({
      id: `prem_cs_101_m${i + 1}`,
      title: [
        "What is an Algorithm?",
        "Measuring Efficiency",
        "Introducing Big O Notation",
        "O(1) - Constant Time",
        "O(n) - Linear Time",
        "O(n^2) - Quadratic Time",
        "O(log n) - Logarithmic Time",
        "O(n log n) - Linearithmic Time",
        "Comparing Complexities",
        "Why Big O Matters"
      ][i],
      introduction: [
          "Welcome to the world of algorithms! In this first module, we'll explore the fundamental concept of what an algorithm is and why it's a cornerstone of computer science and problem-solving.",
          "How can we tell if one algorithm is better than another? This module introduces the idea of algorithmic efficiency, moving beyond simple timers to a more robust, hardware-independent way of measuring performance.",
          "This module introduces the star of our course: Big O Notation. We'll define what it is, why it's the industry standard for talking about efficiency, and understand its core purpose: to describe how performance scales with input size.",
          "We begin our deep dive into specific complexities with the fastest of them all: O(1), or Constant Time. We'll learn to identify operations that take the same amount of time, no matter how much data you throw at them.",
          "Next, we'll examine O(n), or Linear Time, one of the most common complexities. This module will show you how to spot algorithms where the runtime grows in direct proportion to the size of the input data.",
          "Things start to slow down with O(n^2), or Quadratic Time. We'll investigate why nested loops often lead to this complexity and see firsthand how quickly runtime can increase, making it unsuitable for large datasets.",
          "Discover the power of 'divide and conquer' with O(log n), or Logarithmic Time. This module explains how certain clever algorithms can achieve incredible efficiency by repeatedly halving the problem size.",
          "Often found in optimal sorting algorithms, O(n log n) is a hybrid complexity. We'll break down why this 'linearithmic' time is considered a benchmark for efficient sorting and how it balances linear work with logarithmic steps.",
          "It's time for a face-off! We'll visually and conceptually compare the different Big O complexities we've learned, ranking them from fastest to slowest and understanding the dramatic performance differences for large inputs.",
          "In our final module, we'll synthesize everything we've learned. We'll discuss how a solid grasp of Big O Notation is essential for writing scalable code, acing technical interviews, and making informed decisions as a software engineer."
      ][i],
      keyConcepts: [
        [{ title: 'Algorithm Definition', explanation: 'A finite sequence of well-defined, computer-implementable instructions, typically to solve a class of problems or to perform a computation.' }, { title: 'Role in Computing', explanation: 'Algorithms are the building blocks of software, directing the computer on how to process data and produce results.' }],
        [{ title: 'Time Complexity', explanation: 'Measures how the runtime of an algorithm changes as the input size (n) increases.' }, { title: 'Space Complexity', explanation: 'Measures how the memory usage of an algorithm changes as the input size (n) increases.' }],
        [{ title: 'Worst-Case Analysis', explanation: 'Big O focuses on the upper bound of performance, ensuring the algorithm will not perform worse than a certain rate.' }, { title: 'Asymptotic Analysis', explanation: 'It describes the behavior of an algorithm for very large input sizes, ignoring constants and lower-order terms.' }],
        [{ title: 'Independence from Input Size', explanation: 'An O(1) operation completes in the same number of steps regardless of how large the input dataset is.' }, { title: 'Instantaneous Operation', explanation: 'For all practical purposes, these operations are considered instantaneous by the processor.' }],
        [{ title: 'Proportional Growth', explanation: 'If the input size doubles, the number of operations also roughly doubles. The relationship is a straight line on a graph.' }, { title: 'Single Pass', explanation: 'Linear time algorithms typically involve a single loop or pass over all the elements of the input.' }],
        [{ title: 'Nested Iteration', explanation: 'This complexity commonly arises when an algorithm needs to compare every element of a collection to every other element, often via nested loops.' }, { title: 'Exponential Growth', explanation: 'The runtime grows by the square of the input size, leading to very slow performance with large inputs.' }],
        [{ title: 'Halving the Problem', explanation: 'The core principle of logarithmic algorithms is that they discard a significant portion (usually half) of the remaining problem space in each step.' }, { title: 'Prerequisite: Sorted Data', explanation: 'Many O(log n) algorithms, like binary search, require the data to be sorted or structured in a specific way to work.' }],
        [{ title: 'Divide and Conquer Strategy', explanation: 'These algorithms work by breaking the problem down into smaller subproblems (the logarithmic part) and then performing a linear amount of work on each part (the linear part).' }, { title: 'Efficiency in Sorting', explanation: 'This complexity is the best possible average-case time complexity for comparison-based sorting algorithms.' }],
        [{ title: 'Performance Hierarchy', explanation: 'The established ranking from fastest to slowest is O(1), followed by O(log n), O(n), O(n log n), and finally O(n^2).' }, { title: 'Impact of Scale', explanation: 'The difference between complexities might be negligible for a small input size, but becomes enormous as the input size grows into the thousands or millions.' }],
        [{ title: 'Informed Algorithm Choice', explanation: 'Understanding Big O allows developers to select the most appropriate algorithm for the expected data scale.' }, { title: 'Performance Prediction', explanation: 'It enables developers to forecast how their application will behave under heavy load, preventing future bottlenecks.' }]
      ][i],
      practicalExamples: [
        [{ title: 'Recipe Analogy', description: 'A recipe is a perfect real-world algorithm. It has a finite number of steps (add flour, preheat oven) to achieve a specific outcome (bake a cake).' }, { title: 'Simple Code Example', description: 'A function that takes two numbers and returns their sum is a simple algorithm.' }],
        [{ title: 'Timing a Race', description: 'Simply timing a function is like timing a runner. The result depends on external factors (the computer, the weather). We need a better way to measure their inherent capability.' }],
        [{ title: 'Dropping Constants', description: 'An algorithm that takes 2n + 10 steps is simplified to O(n). We only care about the dominant term (n) as the input gets very large.' }],
        [{ title: 'Array Indexing', description: 'Accessing an element in an array, e.g., `myArray[5]`, is O(1). The computer can mathematically calculate the memory address instantly.' }, { title: 'Hash Table Lookup', description: 'Finding a value by its key in a hash table or dictionary is, on average, an O(1) operation.' }],
        [{ title: 'Linear Search', description: 'Finding an item in an unsorted list requires looking at each item one by one. In the worst case, you check all "n" items.' }, { title: 'Printing all elements', description: 'A `for` loop that iterates through an array and prints each element is a classic O(n) operation.' }],
        [{ title: 'Bubble Sort', description: 'The bubble sort algorithm repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order. This requires nested loops, resulting in O(n^2).' }],
        [{ title: 'Binary Search', description: 'Searching for a word in a physical dictionary. You open to the middle, decide if your word is before or after, and then repeat the process on the remaining half. This is O(log n).' }],
        [{ title: 'Merge Sort', description: 'This algorithm divides the array in half, sorts each half recursively, and then merges the sorted halves. The division is the logarithmic part, and the merging is the linear part.' }],
        [{ title: 'Graphing the Growth', description: 'Plotting the graph of "n squared" versus "n times log n" shows that while they might be close for small inputs, the "n squared" line curves up dramatically, demonstrating its inefficiency at scale.' }],
        [{ title: 'Interview Question', description: 'A common interview question is "What is the time complexity of this code snippet?". Being able to identify Big O quickly is a crucial skill for software engineering roles.' }]
      ][i],
      summary: [
          "In summary, an algorithm is a clear set of instructions for solving a problem. They are the fundamental logic behind all computer programs, from the simplest calculator to the most complex operating system.",
          "We've learned that measuring efficiency is key to evaluating algorithms. Rather than just timing them, we focus on how their resource usage (time and memory) scales as the input size grows.",
          "Big O Notation is the mathematical language we use to describe an algorithm's efficiency in its worst-case scenario. It provides a standardized way to compare performance that is independent of hardware.",
          "O(1) or Constant Time is the pinnacle of efficiency. These operations are incredibly fast because their execution time is not affected by the size of the input data. Array access by index is a prime example.",
          "O(n) or Linear Time describes algorithms where performance grows linearly with the input size. These are very common and generally considered efficient for many tasks involving iterating through a collection once.",
          "O(n^2) or Quadratic Time indicates an algorithm whose performance is proportional to the square of the input size. This is often a sign of inefficiency, especially when dealing with large datasets, and should be avoided if possible.",
          "O(log n) or Logarithmic Time algorithms are exceptionally efficient. By repeatedly reducing the size of the problem, they can handle enormous datasets with minimal increases in runtime. Binary search is a classic example.",
          "O(n log n) or Linearithmic Time represents a sweet spot for complex operations like sorting. It's the hallmark of efficient 'divide and conquer' algorithms like Merge Sort and Quick Sort.",
          "By comparing complexities, we've established a clear hierarchy of efficiency. Understanding this hierarchy is crucial for making decisions about which data structures and algorithms to use for a given problem.",
          "Ultimately, understanding Big O Notation is not just an academic exercise. It is a practical and essential skill for any programmer, directly impacting code quality, application performance, and success in technical interviews."
      ][i]
    })),
  },
  {
    id: 'prem_bio_101',
    title: 'Biology 101: The Process of Photosynthesis',
    difficulty: 'Beginner',
    major: 'Biology',
    tags: ['Botany', 'Cell Biology'],
    modules: Array.from({ length: 10 }, (_, i) => ({
      id: `prem_bio_101_m${i + 1}`,
      title: [
        "What is Photosynthesis?",
        "Who Photosynthesizes?",
        "The Chemical Equation",
        "The Chloroplast: Powerhouse of the Plant Cell",
        "Stage 1: Light-Dependent Reactions",
        "The Role of Chlorophyll",
        "Splitting Water: Photolysis",
        "Stage 2: The Calvin Cycle (Light-Independent)",
        "Fixing Carbon Dioxide",
        "Why Photosynthesis is Essential for Life"
      ][i],
      introduction: [
        "This module introduces the remarkable process by which green plants, algae, and some bacteria convert light energy into chemical energy. This chemical energy is stored in the form of glucose (a type of sugar), which the organism can use as food.",
        "We will identify the organisms that perform photosynthesis, known as 'autotrophs' or 'producers' because they create their own food. This includes all green plants (from trees to grass), algae (like seaweed), and a group of bacteria called cyanobacteria.",
        "We'll break down the overall chemical equation for photosynthesis: **6CO₂ + 6H₂O + Light Energy → C₆H₁₂O₆ + 6O₂**. This means Carbon Dioxide plus Water plus Light Energy yields Glucose (sugar) and Oxygen.",
        "Photosynthesis takes place inside specialized organelles called **chloroplasts**. We will explore the structure of chloroplasts, including the thylakoids and stroma, and their roles in the process.",
        "The first stage requires light and occurs in the thylakoid membranes. Here, light energy is captured and used to create two important energy-carrying molecules: **ATP** and **NADPH**.",
        "**Chlorophyll**, the pigment that gives plants their green color, is the key molecule for absorbing light energy. We will learn how it absorbs light in the blue and red parts of the spectrum and reflects green light.",
        "A crucial event in the light-dependent reactions is **photolysis**, the splitting of water molecules (H₂O) using light energy. This process releases electrons, protons, and **oxygen** as a byproduct—the source of the oxygen we breathe!",
        "The second stage, the Calvin Cycle, does not directly need light but relies on the ATP and NADPH created in the first stage. This process occurs in the stroma of the chloroplast.",
        "In the Calvin Cycle, carbon dioxide (CO₂) from the atmosphere is 'fixed'—incorporated into organic molecules. Using the energy from ATP and NADPH, a series of reactions produces **glucose (C₆H₁₂O₆)**.",
        "We'll conclude by understanding why photosynthesis is the foundation of nearly all life on Earth. It produces the food that forms the base of most food chains and releases the oxygen essential for most living organisms."
      ][i],
       keyConcepts: [
        [{ title: 'Energy Conversion', explanation: 'Photosynthesis converts light energy from the sun into chemical energy stored in glucose.' }, { title: 'Autotrophs', explanation: 'Organisms that produce their own food using light, water, carbon dioxide, or other chemicals.' }],
        [{ title: 'Producers', explanation: 'Autotrophs are the producers in a food chain, meaning they create food for other organisms.' }, { title: 'Cyanobacteria', explanation: 'A phylum of bacteria that obtain their energy through photosynthesis, and are the only photosynthetic prokaryotes able to produce oxygen.' }],
        [{ title: 'Reactants', explanation: 'The inputs of the reaction: Carbon Dioxide (6CO₂), Water (6H₂O), and Light Energy.' }, { title: 'Products', explanation: 'The outputs of the reaction: Glucose (C₆H₁₂O₆) and Oxygen (6O₂).' }],
        [{ title: 'Organelles', explanation: 'Specialized structures within a living cell.' }, { title: 'Thylakoids & Stroma', explanation: 'Thylakoids are membrane-bound compartments inside chloroplasts where light-dependent reactions occur. The stroma is the fluid-filled space where the Calvin Cycle takes place.' }],
        [{ title: 'ATP', explanation: 'Adenosine triphosphate is the principal molecule for storing and transferring energy in cells.' }, { title: 'NADPH', explanation: 'Nicotinamide adenine dinucleotide phosphate is another energy-carrying molecule used in anabolic reactions, such as the Calvin Cycle.' }],
        [{ title: 'Pigment', explanation: 'A material that changes the color of reflected or transmitted light as the result of wavelength-selective absorption.' }, { title: 'Absorption Spectrum', explanation: 'The range of wavelengths of light that a pigment can absorb.' }],
        [{ title: 'Photolysis', explanation: 'The decomposition or separation of molecules by the action of light.' }, { title: 'Byproduct', explanation: 'A secondary product made in the synthesis of something else. Oxygen is a vital byproduct of photosynthesis.' }],
        [{ title: 'Light-Independent Reactions', explanation: 'Chemical reactions that convert carbon dioxide and other compounds into glucose, not directly requiring light to proceed.' }, { title: 'Energy Utilization', explanation: 'This stage uses the ATP and NADPH produced in the light-dependent reactions.' }],
        [{ title: 'Carbon Fixation', explanation: 'The process by which inorganic carbon (particularly in the form of carbon dioxide) is converted to organic compounds by living organisms.' }, { title: 'Glucose Production', explanation: 'The end product of the Calvin Cycle is glucose, which the plant uses for energy and growth.' }],
        [{ title: 'Food Chains', explanation: 'Photosynthesis is at the base of almost all food chains, providing the energy that sustains ecosystems.' }, { title: 'Oxygen Production', explanation: 'Photosynthesis is responsible for maintaining the oxygen levels in the Earth\'s atmosphere.' }]
      ][i],
      practicalExamples: [
        [{ title: 'A Plant in the Sun', description: 'A simple houseplant on a windowsill is a perfect example of photosynthesis in action, quietly converting sunlight into the energy it needs to grow.' }],
        [{ title: 'Algae Blooms', description: 'Large blooms of algae in lakes and oceans are massive collections of photosynthetic organisms, often visible from space.' }],
        [{ title: 'Breathing', description: 'Every breath you take is a reminder of photosynthesis. The oxygen you inhale is a product of this process.' }],
        [{ title: 'Plant Cells Under a Microscope', description: 'Observing plant cells under a microscope reveals the tiny green chloroplasts where all the magic happens.' }],
        [{ title: 'Solar Panels', description: 'Solar panels are a man-made analogy for the light-dependent reactions, converting light energy into a usable form (electricity).' }],
        [{ title: 'Green Leaves', description: 'The green color of leaves is direct evidence of chlorophyll reflecting green light while absorbing other colors for energy.' }],
        [{ title: 'Bubbles from Underwater Plants', description: 'The small bubbles you see coming from underwater plants in an aquarium are bubbles of oxygen being released from photolysis.' }],
        [{ title: 'Plant Growth', description: 'The growth of a plant from a tiny seed into a large tree is powered by the glucose produced during the Calvin Cycle.' }],
        [{ title: 'Carbon Sinks', description: 'Forests are often called "carbon sinks" because they absorb vast amounts of CO₂ from the atmosphere for photosynthesis.' }],
        [{ title: 'Fossil Fuels', description: 'Fossil fuels like coal and oil are the stored chemical energy of ancient photosynthetic organisms from millions of years ago.' }]
      ][i],
      summary: [
          "Photosynthesis is the fundamental process that converts light into life-sustaining chemical energy, forming the base of the food web.",
          "This vital process is carried out by autotrophs, including plants, algae, and cyanobacteria, which are the primary producers of the planet.",
          "The balanced chemical equation of photosynthesis summarizes how carbon dioxide and water are transformed into glucose and oxygen using light energy.",
          "Within the plant cell, the chloroplast acts as a miniature factory, with its distinct parts—thylakoids and stroma—hosting the different stages of photosynthesis.",
          "The light-dependent reactions are the initial phase, where solar energy is captured and stored in the temporary energy carriers ATP and NADPH.",
          "Chlorophyll is the master pigment, expertly absorbing light energy and giving the plant world its characteristic green hue.",
          "Photolysis, the light-driven splitting of water, is a critical step that not only provides electrons for the process but also releases the oxygen we breathe.",
          "The Calvin Cycle represents the second phase, where the captured energy is used to convert atmospheric carbon dioxide into glucose.",
          "Through carbon fixation, inorganic CO₂ is transformed into organic sugar molecules, providing the plant with the fuel it needs for growth and metabolism.",
          "In conclusion, photosynthesis is arguably the most important biological process on Earth, providing the food we eat, the oxygen we breathe, and maintaining the balance of our planet's atmosphere."
      ][i]
    })),
  },
  {
    id: 'prem_hist_101',
    title: 'History 101: The Causes of World War I',
    difficulty: 'Beginner',
    major: 'History',
    tags: ['Modern History', 'War'],
    modules: Array.from({ length: 10 }, (_, i) => ({
      id: `prem_hist_101_m${i + 1}`,
      title: [
        "The Concert of Europe: A Fading Harmony", "Militarism: The Great Arms Race", "Alliances: A Tangled Web",
        "Imperialism: The Scramble for Power", "Nationalism: The Balkan Powder Keg", "The July Crisis: Assassination in Sarajevo",
        "The Blank Check: Germany's Gamble", "Declarations of War: The Dominoes Fall", "The Schlieffen Plan: A War of Movement",
        "Stalemate: The Western Front Emerges"
      ][i],
      introduction: [
        "Before the chaos of 1914, Europe was managed by a system of power balancing known as the Concert of Europe. This module explores how this 19th-century system, designed to prevent major wars, began to unravel under the pressures of a new century.",
        "This module examines the destructive cycle of militarism that gripped Europe. We'll explore the naval race between Britain and Germany, the expansion of armies across the continent, and how the glorification of military power made war seem like an acceptable solution to political problems.",
        "Europe was bound by a complex and rigid system of secret alliances. We will untangle the two major blocs—the Triple Alliance (Germany, Austria-Hungary, Italy) and the Triple Entente (France, Russia, Britain)—and analyze how they turned a regional conflict into a world war.",
        "The great powers of Europe were fierce rivals in a global 'scramble' for colonies, resources, and influence, particularly in Africa and Asia. This module investigates how imperial competition fueled tensions and created friction between nations.",
        "Nationalism was a powerful force, both unifying countries like Germany and tearing apart multi-ethnic empires like Austria-Hungary. We will focus on the volatile Balkan region, known as the 'powder keg of Europe,' where Slavic nationalism clashed with imperial ambitions.",
        "The spark that ignited the war. This module provides a minute-by-minute account of the assassination of Archduke Franz Ferdinand of Austria-Hungary in Sarajevo on June 28, 1914, and the immediate diplomatic crisis that followed.",
        "In the crucial days after the assassination, Germany issued a 'blank check' of unconditional support to its ally, Austria-Hungary. We'll analyze this fateful decision and how it escalated the crisis, effectively giving Austria-Hungary permission to go to war with Serbia.",
        "Following the 'blank check,' a series of ultimatums, mobilizations, and declarations of war occurred in rapid succession. This module traces the chain reaction as the alliance systems were activated, dragging nations one by one into the conflict.",
        "Germany's master plan for a swift victory was the Schlieffen Plan, a massive flanking maneuver through neutral Belgium to quickly defeat France. We will examine the logic, assumptions, and ultimate failure of this ambitious military strategy.",
        "The failure of the Schlieffen Plan and the subsequent 'Race to the Sea' led to the establishment of a continuous line of trenches from the Swiss border to the North Sea. This final module explores how the war of movement ground to a halt, creating the brutal, attritional stalemate of the Western Front."
      ][i],
      keyConcepts: [
        [{ title: 'Balance of Power', explanation: 'A state of stability between competing forces. In international politics, it refers to a system where no single state becomes powerful enough to dominate all others.' }, { title: 'Congress of Vienna', explanation: 'An 1815 conference of ambassadors of European states that established the Concert of Europe and a long-term peace plan.' }],
        [{ title: 'Arms Race', explanation: 'A competition between two or more states to have the best armed forces. Each party competes to produce larger numbers of weapons, greater armies, or superior military technology.' }, { title: 'Dreadnought', explanation: 'A new class of battleship launched by Britain in 1906 that rendered all previous warships obsolete, sparking a naval race with Germany.' }],
        [{ title: 'Triple Alliance', explanation: 'A military alliance among Germany, Austria-Hungary, and Italy that lasted from 1882 until the start of World War I in 1914.' }, { title: 'Triple Entente', explanation: 'The informal understanding and alliance between the Russian Empire, the French Third Republic, and Great Britain.' }],
        [{ title: 'The Scramble for Africa', explanation: 'The invasion, occupation, division, and colonization of most of Africa by seven Western European powers during a short period known as New Imperialism (1881-1914).' }, { title: 'Sphere of Influence', explanation: 'A region within one country over which another country claims certain exclusive rights.' }],
        [{ title: 'Pan-Slavism', explanation: 'A political ideology concerned with the advancement of integrity and unity for the Slavic-speaking peoples. It was a major factor in Russia\'s support for Serbia.' }, { title: 'Multi-Ethnic Empire', explanation: 'An empire composed of many different ethnic groups, such as the Austro-Hungarian Empire, which faced constant nationalist unrest.' }],
        [{ title: 'Archduke Franz Ferdinand', explanation: 'The heir presumptive to the throne of Austria-Hungary. His assassination was the proximate cause of World War I.' }, { title: 'The Black Hand', explanation: 'A secret military society formed by members of the Serbian army, responsible for organizing the assassination.' }],
        [{ title: 'Unconditional Support', explanation: 'Germany promised to support Austria-Hungary in whatever action it took against Serbia, without any conditions or limits.' }, { title: 'Escalation', explanation: 'The process of increasing the intensity of a conflict. Germany\'s blank check was a major escalatory step.' }],
        [{ title: 'Mobilization', explanation: 'The act of assembling and making both troops and supplies ready for war. In 1914, mobilization was considered an act of war.' }, { title: 'Chain Reaction', explanation: 'A sequence of events in which each event is the result of the previous one and the cause of the next.' }],
        [{ title: 'War on Two Fronts', explanation: 'A war in which fighting takes place on two geographically separate fronts. Germany feared a two-front war against both France and Russia.' }, { title: 'Neutrality of Belgium', explanation: 'Belgium was officially a neutral country, and Germany\'s invasion of it was the final act that brought Great Britain into the war.' }],
        [{ title: 'Trench Warfare', explanation: 'A type of land warfare using occupied fighting lines consisting largely of military trenches, in which troops are well-protected from the enemy\'s small arms fire and are substantially sheltered from artillery.' }, { title: 'War of Attrition', explanation: 'A military strategy consisting of belligerent attempts to win a war by wearing down the enemy to the point of collapse through continuous losses in personnel and materiel.' }]
      ][i],
      practicalExamples: [
// Fix: Changed outer single quotes to double quotes to avoid parsing errors with escaped single quotes.
        [{ title: 'A See-Saw', description: "The balance of power worked like a see-saw, with nations shifting alliances to prevent any one side from getting too 'heavy' or powerful." }],
        [{ title: 'Schoolyard Bullies', description: 'The arms race was like schoolyard bullies showing off their strength. Each nation built bigger armies and navies not just for defense, but to intimidate rivals.' }],
        [{ title: 'Chain Gang', description: 'The alliance system acted like a chain gang. When one member got into a fight (Austria-Hungary), all the others were dragged along with it.' }],
        [{ title: 'A Monopoly Board', description: 'The world map was like a Monopoly board for European powers, competing to acquire the most valuable properties (colonies) around the globe.' }],
// Fix: Changed outer single quotes to double quotes to avoid parsing errors with escaped single quotes.
        [{ title: 'A Family Feud', description: "The Balkans were like a massive, interconnected family feud, with different ethnic groups (the 'family members') fighting for independence from the empires that controlled them." }],
// Fix: Changed outer single quotes to double quotes to avoid parsing errors with escaped single quotes.
        [{ title: 'A Single Match', description: "The assassination was the single match that lit the fuse of the Balkan 'powder keg', causing an explosion that engulfed all of Europe." }],
// Fix: Changed outer single quotes to double quotes to avoid parsing errors with escaped single quotes.
        [{ title: 'A Co-signed Loan', description: "Germany's 'blank check' was like co-signing a loan for a reckless friend. They gave their support without knowing how Austria-Hungary would 'spend' it, and were ultimately responsible for the consequences." }],
        [{ title: 'Falling Dominoes', description: 'Once Austria-Hungary declared war on Serbia, the alliances caused the great powers to fall like dominoes into war: Russia mobilized to protect Serbia, Germany declared war on Russia, France declared war on Germany, and so on.' }],
        [{ title: 'A Revolving Door', description: 'The Schlieffen Plan was designed to be like a revolving door, swinging through Belgium to quickly knock out France before turning to face the slower-mobilizing Russia.' }],
        [{ title: 'A Tug of War', description: 'The Western Front became a giant, static tug of war, with neither side able to pull the other out of their deeply dug-in trench positions, leading to years of bloody stalemate.' }]
      ][i],
      summary: [
        "The 19th-century system of diplomatic cooperation, the Concert of Europe, had become too fragile to handle the intense rivalries of the early 20th century, setting the stage for a major conflict.",
        "A rampant arms race, particularly the Anglo-German naval competition, normalized massive military spending and fostered a culture where war was seen as a viable tool of state policy.",
        "The rigid, two-camp alliance system (Triple Alliance vs. Triple Entente) created a situation where a small, regional dispute could almost automatically escalate into a continent-wide war.",
        "Intense competition for colonies and economic resources across the globe created numerous points of friction and mistrust among the European great powers.",
        "The force of nationalism was a double-edged sword: while it built nations, it also threatened to tear apart the Austro-Hungarian and Ottoman empires, making the Balkans an incredibly unstable region.",
        "The assassination of Archduke Franz Ferdinand by a Serbian nationalist group provided the perfect pretext for Austria-Hungary to attempt to crush Serbia, setting off the July Crisis.",
        "Germany's unconditional promise of support to Austria-Hungary was a critical turning point, empowering Vienna to take a hard line and dramatically escalating the diplomatic crisis beyond a regional issue.",
        "In a tragic and seemingly unstoppable sequence, the activation of the alliance systems following Austria-Hungary's declaration of war on Serbia pulled all of Europe's major powers into the conflict within a matter of weeks.",
        "Germany's plan for a quick victory by invading France through Belgium failed, and its violation of Belgian neutrality ensured Great Britain's entry into the war, making the conflict truly global.",
        "The initial war of rapid movement quickly devolved into a static and brutal war of attrition, characterized by trench warfare on the Western Front, which would define the conflict for the next four years."
      ][i]
    })),
  },
  {
    id: 'prem_cs_102',
    title: 'Data Structures 102: Arrays vs. Linked Lists',
    difficulty: 'Intermediate',
    major: 'Computer Science',
    tags: ['Data Structures', 'Fundamentals'],
    modules: Array.from({ length: 10 }, (_, i) => ({
      id: `prem_cs_102_m${i + 1}`,
      title: "Module " + (i+1),
      introduction: "This is the introduction for module " + (i+1),
      keyConcepts: [{title: "KC1", explanation: "Expl 1"}, {title: "KC2", explanation: "Expl 2"}],
      practicalExamples: [{title: "PE1", description: "Desc 1"}, {title: "PE2", description: "Desc 2"}],
      summary: "This is the summary for module " + (i+1),
    })),
  },
  {
    id: 'prem_bus_101',
    title: 'Business 101: The 4 Ps of Marketing',
    difficulty: 'Beginner',
    major: 'Business',
    tags: ['Marketing', 'Strategy'],
    modules: Array.from({ length: 10 }, (_, i) => ({
      id: `prem_bus_101_m${i + 1}`,
       title: [
        "What is the Marketing Mix?", "Product: Creating Value", "Price: Capturing Value",
        "Place: Delivering Value", "Promotion: Communicating Value", "The Interplay of the 4 Ps",
        "Target Markets and Segmentation", "Case Study: Apple's Marketing Mix", "The Digital Shift: The 4 Ps Online",
        "Beyond the 4 Ps: The 7 Ps of Services"
      ][i],
      introduction: [
        "Welcome to the cornerstone of marketing strategy! This module introduces the 'Marketing Mix,' a foundational model that businesses use to bring a product or service to market. We'll define the four key elements—Product, Price, Place, and Promotion—that every marketer must manage.",
        "What are you actually selling? This module dives deep into the 'Product' element. It's more than just a physical item; it includes design, features, quality, branding, and packaging. We'll explore how to create a product that meets customer needs and stands out from the competition.",
        "How much is your product worth? 'Price' is the only 'P' that generates revenue. We'll analyze different pricing strategies, from budget-friendly to premium, and discuss how price signals quality, affects demand, and determines profitability.",
        "Where and how do customers get your product? 'Place' refers to distribution channels and logistics. This module covers everything from physical retail stores to e-commerce websites, ensuring the product is available to customers at the right place and time.",
        "How do you tell the world about your product? 'Promotion' is all about communication. We'll explore the promotional mix, including advertising, public relations, sales promotions, and personal selling, to see how businesses create awareness and persuade customers to buy.",
        "The 4 Ps don't work in isolation; they are deeply interconnected. This module focuses on how a change in one 'P' affects the others. We'll see how a premium product requires a high price, selective placement, and sophisticated promotion to create a coherent strategy.",
        "You can't sell to everyone. This module introduces the crucial concepts of market segmentation and targeting. We'll learn how businesses divide a broad market into smaller groups of consumers with similar needs and then tailor their marketing mix to a specific target segment.",
        "Let's see the 4 Ps in action with one of the world's most successful companies. We will analyze Apple's marketing mix for the iPhone, deconstructing how its premium product, high price, selective retail placement, and iconic promotional campaigns work together seamlessly.",
        "The internet has revolutionized marketing. This module explores how the 4 Ps have evolved in the digital age. We'll discuss how 'Place' becomes a website, 'Promotion' involves social media marketing, and customer reviews impact 'Product' and 'Price'.",
        "Is the 4 P model enough? For services like consulting, hospitality, or banking, an expanded model is often used. This final module introduces the '7 Ps of Services Marketing,' adding People, Process, and Physical Evidence to the original mix."
      ][i],
      keyConcepts: [
        [{ title: 'Marketing Mix', explanation: 'The set of tactical marketing tools – Product, Price, Place, and Promotion – that the firm blends to produce the response it wants in the target market.' }, { title: '4 Ps Model', explanation: 'A framework developed by E. Jerome McCarthy that provides a structure for marketing decision-making.' }],
        [{ title: 'Core Product vs. Augmented Product', explanation: 'The core product is the basic benefit the customer is buying. The augmented product includes the additional features and services that differentiate it.' }, { title: 'Branding', explanation: 'The process of creating a strong, positive perception of a company, its products or services in the customer\'s mind.' }],
        [{ title: 'Cost-Plus Pricing', explanation: 'A pricing strategy where the selling price is determined by adding a specific markup percentage to a product\'s unit cost.' }, { title: 'Value-Based Pricing', explanation: 'A strategy of setting prices primarily based on a consumer\'s perceived value of a product or service.' }],
        [{ title: 'Distribution Channels', explanation: 'The path through which goods and services travel from the vendor to the consumer. Examples include wholesalers, retailers, and e-commerce.' }, { title: 'Logistics', explanation: 'The detailed coordination of a complex operation involving many people, facilities, or supplies.' }],
        [{ title: 'Promotional Mix', explanation: 'The blend of promotional variables chosen by marketers to help a firm reach its goals. It includes advertising, PR, sales promotion, and direct marketing.' }, { title: 'Integrated Marketing Communications (IMC)', explanation: 'Ensuring the consistency of message and the complementary use of media across all promotional tools.' }],
        [{ title: 'Strategic Coherence', explanation: 'Ensuring that all elements of the marketing mix are consistent and work together to support the overall business strategy and brand positioning.' }, { title: 'Synergy', explanation: 'The concept that the combined effect of the 4 Ps is greater than the sum of their individual effects.' }],
        [{ title: 'Market Segmentation', explanation: 'The process of dividing a broad consumer or business market into sub-groups of consumers based on some type of shared characteristics.' }, { title: 'Target Market', explanation: 'A specific group of consumers at which a company aims its products and services.' }],
        [{ title: 'Premium Branding', explanation: 'Positioning a product as high-quality and high-value, which justifies a higher price point.' }, { title: 'Ecosystem Strategy', explanation: 'Creating a network of interconnected products and services that work together, encouraging customers to stay within the brand (e.g., iPhone, Mac, Apple Watch).' }],
        [{ title: 'E-commerce', explanation: 'The buying and selling of goods or services using the internet, and the transfer of money and data to execute these transactions.' }, { title: 'Content Marketing', explanation: 'A marketing strategy focused on creating and distributing valuable, relevant, and consistent content to attract and retain a clearly defined audience.' }],
        [{ title: 'People', explanation: 'All human actors who play a part in the service delivery and thus influence the buyer’s perceptions.' }, { title: 'Process & Physical Evidence', explanation: 'The procedures by which a service is delivered, and the environment in which the service is delivered and where the firm and customer interact.' }]
      ][i],
      practicalExamples: [
        [{ title: 'A Cup of Coffee', description: "The coffee itself is the product, the $4 charge is the price, the café is the place, and the '2-for-1' sign is the promotion. All four work together in your decision to buy." }],
        [{ title: 'A Car', description: 'The core product is transportation. The augmented product includes the leather seats, the satellite radio subscription, the warranty, and the brand image of the car.' }],
        [{ title: 'Movie Theater Tickets', description: 'A theater uses dynamic pricing: tickets are more expensive on a Friday night (high demand) and cheaper for a Tuesday matinee (low demand).' }],
        [{ title: 'Coca-Cola', description: "Coca-Cola uses an intensive distribution strategy. Their 'Place' is everywhere: supermarkets, vending machines, restaurants, and gas stations, making it available whenever a customer is thirsty." }],
        [{ title: 'Nike', description: 'Nike uses a mix of promotions: high-budget TV commercials with star athletes (advertising), sponsoring events (public relations), and a powerful social media presence (digital marketing).' }],
        [{ title: 'Luxury Watches', description: "A Rolex watch (premium Product) has a very high Price, is sold only in exclusive jewelry stores (Place), and is advertised in luxury magazines (Promotion). The whole mix screams exclusivity." }],
// Fix: Changed outer single quotes to double quotes to avoid parsing errors with escaped single quotes.
        [{ title: 'A Fitness Company', description: "They might segment the market into 'young athletes,' 'busy parents,' and 'active seniors.' They would then target the 'busy parents' segment with a marketing mix featuring quick, at-home workouts." }],
        [{ title: 'iPhone Pricing', description: "Apple sets a high price for the iPhone (Price) because its innovative features and sleek design (Product) create a high perceived value, which is reinforced by its artistic commercials (Promotion) and sold in pristine Apple Stores (Place)." }],
        [{ title: 'Amazon', description: 'Amazon is a master of \'Place\' in the digital world, with its one-click ordering and fast delivery. Its \'Promotion\' is highly personalized through its recommendation engine.' }],
// Fix: Changed outer single quotes to double quotes to avoid parsing errors with escaped single quotes.
        [{ title: 'A High-End Restaurant', description: "The food is the 'Product,' but the experience is shaped by the attentive waiters ('People'), the efficient reservation system ('Process'), and the beautiful decor ('Physical Evidence')." }]
      ][i],
      summary: [
        "The Marketing Mix, or the 4 Ps, is a fundamental framework that helps businesses structure their approach to the market. Mastering Product, Price, Place, and Promotion is the first step toward a successful marketing strategy.",
        "The 'Product' is the core of the marketing mix. A successful product must provide real value and solve a problem for the customer, going beyond its physical attributes to include branding and customer experience.",
        "'Price' is a critical strategic lever. It must reflect the product's value, cover costs, and align with the company's market position, all while being acceptable to the target customer.",
        "'Place' ensures that the product is accessible. An effective distribution strategy gets the product to the right customers through the right channels at the right time, whether online or in a physical store.",
        "'Promotion' is the voice of your product. A well-planned promotional strategy uses a blend of tools like advertising and social media to build awareness, create desire, and drive sales.",
        "The true power of the marketing mix lies in its integration. Each of the 4 Ps must be consistent and work in synergy with the others to create a strong, coherent, and effective market offering.",
        "No business can appeal to everyone. Effective marketing requires segmenting the market into distinct groups and selecting a specific target market to serve, tailoring the 4 Ps to their unique needs.",
        "Global brands like Apple provide a masterclass in the 4 Ps. Their success is built on a perfectly aligned marketing mix where every element reinforces the others to create an incredibly powerful brand and desirable products.",
        "The rise of the internet has transformed the 4 Ps, creating new channels for 'Place' (e-commerce) and 'Promotion' (digital marketing) and giving consumers more power over 'Product' (reviews) and 'Price' (comparison tools).",
        "For service-based businesses, the 4 Ps are often expanded to 7 Ps. The addition of People, Process, and Physical Evidence helps marketers manage the intangible aspects of delivering a high-quality service experience."
      ][i]
    })),
  }
];```

---

## index.tsx

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
// Fix: Add .tsx file extension for component import
import App from './App.tsx';
import { preventDoubleTapZoom } from './utils/mobileUtils';

console.log('React app starting...');

// Initialize mobile enhancements
if (typeof document !== 'undefined') {
  preventDoubleTapZoom();
  
  // Prevent pull-to-refresh on mobile
  document.body.style.overscrollBehavior = 'none';
  
  // Optimize for mobile performance
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      // Preconnect to external resources
      const preconnectDomains = [
        'https://fonts.googleapis.com',
        'https://fonts.gstatic.com',
        'https://cdn.tailwindcss.com'
      ];
      preconnectDomains.forEach(domain => {
        const link = document.createElement('link');
        link.rel = 'preconnect';
        link.href = domain;
        link.crossOrigin = 'anonymous';
        document.head.appendChild(link);
      });
    });
  }
}

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

console.log('Root element found, rendering app...');

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

## utils/mobileUtils.ts

```typescript
/**
 * Triggers a short haptic feedback vibration on supported mobile devices.
 * Checks for the presence of the navigator.vibrate API before attempting to use it.
 * @param {number} duration - The duration of the vibration in milliseconds. Defaults to 50ms.
 */
export const triggerHapticFeedback = (duration: number = 50): void => {
    if (typeof window !== 'undefined' && window.navigator && 'vibrate' in window.navigator) {
        try {
            window.navigator.vibrate(duration);
        } catch (e) {
            // Some browsers might throw an error if the user has disabled vibrations.
            console.warn("Haptic feedback failed.", e);
        }
    }
};

/**
 * Checks if the current device is a mobile device
 */
export const isMobileDevice = (): boolean => {
    if (typeof window === 'undefined') return false;
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           (navigator.maxTouchPoints && navigator.maxTouchPoints > 2 && /MacIntel/.test(navigator.platform));
};

/**
 * Gets the viewport height accounting for mobile browser UI
 */
export const getViewportHeight = (): number => {
    if (typeof window === 'undefined') return 0;
    return window.visualViewport?.height || window.innerHeight;
};

/**
 * Prevents zoom on double tap for mobile devices
 */
export const preventDoubleTapZoom = (): void => {
    if (typeof document === 'undefined') return;
    
    let lastTouchEnd = 0;
    document.addEventListener('touchend', (event) => {
        const now = Date.now();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
};

/**
 * Detects swipe gestures
 */
export const detectSwipe = (
    element: HTMLElement,
    onSwipeLeft?: () => void,
    onSwipeRight?: () => void,
    threshold: number = 50
): (() => void) => {
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    const handleTouchStart = (e: TouchEvent) => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    };

    const handleTouchEnd = (e: TouchEvent) => {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
    };

    const handleSwipe = () => {
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;

        // Only trigger if horizontal swipe is greater than vertical
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > threshold) {
            if (deltaX > 0 && onSwipeRight) {
                onSwipeRight();
                triggerHapticFeedback();
            } else if (deltaX < 0 && onSwipeLeft) {
                onSwipeLeft();
                triggerHapticFeedback();
            }
        }
    };

    element.addEventListener('touchstart', handleTouchStart);
    element.addEventListener('touchend', handleTouchEnd);

    // Return cleanup function
    return () => {
        element.removeEventListener('touchstart', handleTouchStart);
        element.removeEventListener('touchend', handleTouchEnd);
    };
};
```

---

## utils/promptGenerator.ts

```typescript
// Fix: Add .ts file extension for type import
import { UserProfile } from '../types.ts';

// A curated list of topics for a few majors to make suggestions more concrete.
const TOPICS_BY_MAJOR: { [key: string]: { introductory: string[], advanced: string[] } } = {
  'Computer Science': {
    introductory: ['the importance of data structures', 'the evolution of programming languages'],
    advanced: ['the ethical implications of AI', 'the future of quantum computing', 'decentralized autonomous organizations (DAOs)']
  },
  'History': {
    introductory: ['the causes of World War I', 'the significance of the Silk Road'],
    advanced: ['post-colonial theory in African history', 'the economic impact of the Black Death', 'the role of propaganda in the Cold War']
  },
  'Biology': {
    introductory: ['the process of photosynthesis', 'the basics of cell theory'],
    advanced: ['the applications of CRISPR gene editing', 'the role of epigenetics in disease', 'the challenges of antibiotic resistance']
  },
  'Business': {
    introductory: ['the four Ps of marketing', 'the concept of supply and demand'],
    advanced: ['the impact of globalization on supply chains', 'strategies for entering emerging markets', 'the valuation of tech startups']
  },
  'Psychology': {
    introductory: ['classical vs. operant conditioning', 'the stages of cognitive development'],
    advanced: ['the neuroscience of memory', 'the effectiveness of cognitive behavioral therapy (CBT)', 'the nature vs. nurture debate in intelligence']
  },
};

const getRandomItem = <T>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];

// Generates highly relevant and intelligent prompt suggestions based on user data.
export const generateSmartPrompts = (user: UserProfile, toolId: string): string[] => {
  const { major, academicYear, goals } = user;
  
  const isEarlyYears = academicYear === 'Freshman' || academicYear === 'Sophomore';
  const majorTopics = TOPICS_BY_MAJOR[major] || { introductory: ['a foundational concept in your field'], advanced: ['an advanced topic in your field'] };
  const topic = getRandomItem(isEarlyYears ? majorTopics.introductory : majorTopics.advanced);

  const goalBasedPrompts: { [key: string]: string[] } = {
    'Improve Writing Skills': [
      `Help me strengthen the thesis statement for an essay about "${topic}".`,
      `Rephrase this sentence for a more academic tone: "I think the author is basically trying to say..."`,
    ],
    'Prepare for Career': [
      `How can I connect my studies on "${topic}" to my career goals?`,
      `Draft a LinkedIn post about a project I completed related to ${major.toLowerCase()}.`
    ],
    'Boost Productivity': [
      `Break down the process of writing a research paper on "${topic}" into manageable steps.`,
      `Generate a 5-point checklist for proofreading my assignments.`,
    ],
    'Manage Study Stress': [
      `I'm feeling overwhelmed with my workload in ${major}. Can you offer some encouragement?`,
      `Guide me through a quick breathing exercise to focus before studying.`,
    ],
  };

  // Select one goal-based prompt if a relevant goal exists
  const relevantGoal = goals.find(g => goalBasedPrompts[g]);
  const goalPrompt = relevantGoal ? getRandomItem(goalBasedPrompts[relevantGoal]) : null;

  let prompts: string[] = [];

  switch (toolId) {
    case 'essay-writer':
      prompts = [
        `Generate an essay outline on the topic: "${topic}".`,
        `Write an introductory paragraph for a paper about the main challenges in ${major.toLowerCase()} today.`,
        `Analyze the impact of a key historical event on the field of ${major.toLowerCase()}.`
      ];
      break;
    case 'debate-partner-ai':
        prompts = [
            `Let's debate the topic: "${topic}". I'll argue in favor of it.`,
            `Help me prepare for a class debate by challenging my position on a controversial issue in ${major}.`,
            `I need to strengthen my argument for my thesis. Act as a skeptical reviewer.`
        ];
        break;
    case 'plagiarism-checker':
      prompts = [
        `Check this paragraph from my ${major} essay for plagiarism.`,
        `Can you scan my lab report introduction for any unintentional plagiarism?`,
        `Review this literature review section and suggest citations.`
      ];
      break;
     case 'grant-proposal-pro':
        prompts = [
            `Help me start a grant proposal for a research project on "${topic}".`,
            `What are the key components of a successful grant application in the field of ${major}?`,
            `Draft a 'Problem Statement' for a grant proposal about a current issue in my field.`
        ];
        break;
     case 'litreview-synthesizer':
        prompts = [
            `Create a literature review outline for a paper on "${topic}".`,
            `Identify the key themes and research gaps for a literature review in my area of study.`,
            `Who are the seminal authors I must include in a review of literature on ${major.toLowerCase()}?`
        ];
        break;
    case 'email-composer':
      prompts = [
        `Compose a formal email to a professor asking for an extension on my ${major} assignment.`,
        `Write a networking email to an alumnus from ${user.university} who works in my target industry.`,
        `Draft an email to my group project members to coordinate our next meeting.`
      ];
      break;
    case 'resume-builder':
      const roleType = isEarlyYears ? 'an internship' : 'a full-time role';
      prompts = [
        `Create 3 resume bullet points for a project on "${topic}".`,
        `Write a professional summary for a ${academicYear.toLowerCase()} student in ${major} seeking ${roleType}.`,
        `What are the top 5 skills I should list on my resume for the ${major.toLowerCase()} industry?`
      ];
      break;
    case 'interview-simulator':
        const interviewTypeSim = isEarlyYears ? 'an internship interview' : 'a graduate role interview';
        prompts = [
            `Let's simulate ${interviewTypeSim} for a company in the ${major.toLowerCase()} industry.`,
            `Ask me some tough behavioral questions for a role I'm applying for.`,
            `Help me practice my "Tell me about yourself" pitch for a job interview.`
        ];
        break;
    case 'linkedin-optimizer':
      const linkedinRole = isEarlyYears ? 'an internship role' : 'a graduate position';
      prompts = [
        `Help me write a compelling 'About' section for my LinkedIn profile.`,
        `Optimize my LinkedIn headline for a ${academicYear.toLowerCase()} ${major} student seeking ${linkedinRole}.`,
        `What are 5 keywords I should include in my profile to attract recruiters for the ${major.toLowerCase()} industry?`
      ];
      break;
    case 'mindfulness-coach':
      prompts = [
        `Guide me through a 5-minute meditation to reduce stress about my ${major} exams.`,
        `I'm having trouble focusing on my studies. Can you lead a short mindfulness exercise?`,
        `Help me with a visualization exercise to prepare for an important presentation.`
      ];
      break;
    case 'sim-coach':
      prompts = [
        `As a ${academicYear.toLowerCase()} ${major} student, how can I manage my time better?`,
        `I'm feeling impostor syndrome. Can you give me some advice?`,
        `What are some effective study techniques for difficult subjects in ${major.toLowerCase()}?`
      ];
      break;
    case 'cognitive-reframer':
        prompts = [
            `I'm stressed about an upcoming exam. Help me reframe my negative thoughts.`,
            `I made a mistake on an assignment and feel like a failure. Can we work through this thought?`,
            `Help me identify the cognitive distortion in this thought: "If I don't get a perfect grade, I'm worthless."`
        ];
        break;
     case 'habit-architect':
        prompts = [
            `I want to build a consistent habit of studying every day. Help me create a plan.`,
            `Help me break my habit of procrastinating on my ${major} assignments.`,
            `Design a plan for me to start waking up earlier using the Four Laws of Behavior Change.`
        ];
        break;
    case 'study-planner':
      prompts = [
          `Create a weekly study plan for my ${major} courses.`,
          `I have 3 exams in the next 10 days. Help me create a cram schedule.`,
          `How can I balance my part-time job with studying for my ${major} degree?`
      ];
      break;
    case 'presentation-helper':
        prompts = [
            `Create a 5-slide outline for a presentation on "${topic}".`,
            `Give me tips on how to make my ${major} presentation more engaging for a non-expert audience.`,
            `Help me write a compelling opening for a presentation about my capstone project.`
        ];
        break;
     case 'conflict-resolution-coach':
        prompts = [
            `I need to have a difficult conversation with my project partner about their lack of contribution.`,
            `Help me prepare to talk to my roommate about noise levels.`,
            `How can I use "I" statements to express my feelings without blaming someone?`
        ];
        break;
    case 'public-speaking-pro':
        prompts = [
            `Review my speech for my ${major} class and suggest improvements.`,
            `Help me make the conclusion of my presentation more impactful.`,
            `Generate some potential audience questions for a talk on "${topic}".`
        ];
        break;
    case 'concept-explainer':
        prompts = [
            `Explain "${topic}" like I'm a complete beginner.`,
            `Use an analogy to explain a complex theory in ${major.toLowerCase()}.`,
            `What is the real-world application of the concepts I'm learning in my ${major} degree?`
        ];
        break;
    case 'study-buddy':
        prompts = [
            `Give me a 5-question practice quiz on "${topic}".`,
            `Let's do a practice exam on the fundamentals of ${major.toLowerCase()}.`,
            `Test my knowledge on a key concept for my ${academicYear} ${major} class.`
        ];
        break;
     case 'mind-meld':
        prompts = [
            `Let's have a study group session on the topic: "${topic}".`,
            `I need to understand the different perspectives on a key debate in ${major.toLowerCase()}.`,
            `Help me prepare for a discussion-based exam by exploring a complex theory.`
        ];
        break;
    case 'career-compass':
        prompts = [
            `Model a 5-year career path for a ${major.toLowerCase()} student like me.`,
            `I want to work in a creative industry. Can you build a roadmap for me?`,
            `What skills should I focus on for the next two years to maximize my career potential?`
        ];
        break;
    case 'syllabus-synthesizer':
        prompts = [
            `Generate a 10-week syllabus for an introductory course on "${topic}".`,
            `Create a course structure for an advanced seminar in ${major.toLowerCase()}.`,
            `I want to self-study a new subject. Can you create a syllabus to guide me?`
        ];
        break;
    case 'socratic-tutor':
        prompts = [
            `I'm stuck on a homework problem about "${topic}". Can you help me think through it?`,
            `I don't understand a core concept in my ${major} class. Ask me questions to help me learn.`,
            `Help me prepare for an exam by testing my understanding with guiding questions.`
        ];
        break;
     case 'learning-style-assessor':
        prompts = [
            `Let's figure out my learning style.`,
            `I want to find more effective study methods. Can you assess my learning style?`,
            `Ask me some questions to determine if I'm a visual, auditory, or kinesthetic learner.`
        ];
        break;
    case 'textbook-arbitrage':
        prompts = [
            `Find the cheapest option for my required ${major.toLowerCase()} textbook this semester.`,
            `Is it better to rent or buy textbooks for my ${academicYear} year courses?`,
            `Analyze the cost of digital vs. physical textbooks for my upcoming classes.`
        ];
        break;
    case 'student-loan-optimizer':
      if (isEarlyYears) {
          prompts = [
              `Explain the difference between subsidized and unsubsidized student loans.`,
              `What are some good financial habits I can start now to minimize my future student debt?`,
              `What is a 529 plan and how does it work?`
          ];
      } else if (academicYear === 'Graduate') {
          prompts = [
            `Model a payment strategy for my graduate school loans.`,
            `Am I eligible for any loan forgiveness programs with a graduate degree in ${major}?`,
            `Compare income-driven repayment plans for my situation.`
          ];
      }
      else { // Junior, Senior
          prompts = [
              `Help me create a budget to start paying off my loans after I graduate.`,
              `Should I consider refinancing my student loans? What are the pros and cons?`,
              `What is a loan grace period and how should I prepare for it?`
          ];
      }
      break;
    case 'scholarship-engine':
        prompts = [
            `Find scholarships for a ${academicYear.toLowerCase()} majoring in ${major}.`,
            `Help me write an essay for a scholarship focused on leadership skills.`,
            `What are some common mistakes to avoid when applying for scholarships?`,
        ];
        break;
    case 'budget-builder-ai':
        prompts = [
            `Help me create a monthly budget based on my part-time job income.`,
            `I want to save for a new laptop. Can you help me build a budget?`,
            `Let's create a 50/30/20 budget for a typical ${academicYear} student.`
        ];
        break;
    case 'investment-illustrator':
        prompts = [
            `Explain compound interest to me using an analogy from ${major}.`,
            `What is a Roth IRA? Explain it like I'm a ${academicYear}.`,
            `Use a simple metaphor to explain the concept of risk diversification.`
        ];
        break;
    case 'gig-economy-maximizer':
      const skillFromMajor = {
        'Computer Science': 'coding',
        'Business': 'market research',
        'History': 'research and writing',
        'Psychology': 'user research',
        'Biology': 'scientific writing or data entry',
      }[major] || 'skills related to your major';

      prompts = [
        `How can I find freelance ${skillFromMajor} gigs?`,
        `Help me create a plan to balance my ${academicYear} coursework with a side hustle.`,
        `What are some simple ways to track my income and expenses for tax purposes?`
      ];
      break;
    default:
      prompts = [`How can you help me with my ${major.toLowerCase()} studies?`];
  }
  
  // Add the goal-based prompt to the list if it exists, ensuring no duplicates and shuffling
  if (goalPrompt && !prompts.includes(goalPrompt)) {
    prompts.push(goalPrompt);
  }

  // Shuffle and return the top 3 prompts
  return prompts.sort(() => 0.5 - Math.random()).slice(0, 3);
};```

---

## utils/fileUtils.ts

```typescript
export const fileToBase64 = (file: File): Promise<string> => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
        const result = reader.result as string;
        resolve(result.split(',')[1]);
    };
    reader.onerror = error => reject(error);
});

export const readFileAsText = (file: File): Promise<string> => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsText(file);
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = error => reject(error);
});
```

---

## components/Dashboard.tsx

```typescript
import React, { useState } from 'react';
import { UserProfile, Quest, Tool, Rank, Course } from '../types.ts';
import { ALL_TOOLS, RANKS } from '../constants.tsx';
import ParticleEffect from './ParticleEffect.tsx';
import AnimatedProgressBar from './AnimatedProgressBar.tsx';
import { Sparkles, Flame, Bell, Target, Edit3, ChevronRight, LogOut, User as UserIcon, Medal, Footprints, GraduationCap, Play, ShoppingCart, Loader } from './icons.tsx';
import { triggerHapticFeedback } from '../utils/mobileUtils.ts';

interface DashboardProps {
  user: UserProfile | null;
  activeQuests: Quest[];
  toolStats: {[key:string]: {usage: number, streak: number}};
  onSelectTool: (tool: Tool) => void;
  onLogout: () => void;
  onOpenProfile: () => void;
  onOpenStore: () => void;
  onPlayCourse: (course: Course) => void;
  onEditCourse: (course: Course) => void;
  onCreateCourse: () => void;
  onRefreshQuests: () => void;
}

const getUserRank = (level: number): Rank => {
  return RANKS.reduce((rank, current) => 
    level >= current.minLevel ? current : rank, RANKS[0]
  );
};

const Dashboard: React.FC<DashboardProps> = ({ user, activeQuests, toolStats, onSelectTool, onLogout, onOpenProfile, onOpenStore, onPlayCourse, onEditCourse, onCreateCourse, onRefreshQuests }) => {
  const [activeCategory, setActiveCategory] = useState('All');
  const [activeDropdown, setActiveDropdown] = useState<'user' | 'notifications' | null>(null);
  const [hasNewNotifications, setHasNewNotifications] = useState(true);
  
  // State for pull-to-refresh
  const [pullStartY, setPullStartY] = useState<number | null>(null);
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const currentRank = getUserRank(user?.level || 1);
  
  const rankColors: { [key: string]: string } = {
    gray: 'from-gray-600 to-gray-400',
    green: 'from-green-600 to-green-400',
    blue: 'from-blue-600 to-blue-400',
    purple: 'from-purple-600 to-purple-400',
    yellow: 'from-yellow-500 to-yellow-300',
  };

  const handleUserMenuToggle = () => {
    triggerHapticFeedback();
    setActiveDropdown(activeDropdown === 'user' ? null : 'user');
  };

  const handleNotificationsToggle = () => {
      triggerHapticFeedback();
      setActiveDropdown(activeDropdown === 'notifications' ? null : 'notifications');
      if (hasNewNotifications) {
          setHasNewNotifications(false);
      }
  };
  
  const handleTouchStart = (e: React.TouchEvent<HTMLDivElement>) => {
      // Only track pull if user is at the top of the page
      if (window.scrollY === 0) {
          setPullStartY(e.touches[0].clientY);
      }
  };

  const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
      if (pullStartY === null) return;
      const currentY = e.touches[0].clientY;
      const distance = currentY - pullStartY;
      if (distance > 0) { // Only track downward pulls
          e.preventDefault();
          setPullDistance(distance);
      }
  };

  const handleTouchEnd = () => {
      if (pullDistance > 100) { // Refresh threshold
          setIsRefreshing(true);
          triggerHapticFeedback();
          setTimeout(() => {
              onRefreshQuests();
              setIsRefreshing(false);
          }, 1500); // Simulate network delay
      }
      setPullStartY(null);
      setPullDistance(0);
  };

  if (!user) return null;

  const filteredTools = activeCategory === 'All' ? ALL_TOOLS : ALL_TOOLS.filter(tool => tool.category === activeCategory);
  const toolCategories = ['All', 'Writing', 'Career', 'Wellness', 'Communication', 'Financial', 'Education'];

  return (
    <div
      className="min-h-screen bg-black text-white relative"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <div className="fixed inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-black to-pink-900/10" />
        <ParticleEffect />
      </div>

      {isRefreshing && (
          <div className="fixed top-8 left-1/2 -translate-x-1/2 z-50 bg-black/50 backdrop-blur-md p-3 rounded-full" style={{ top: `calc(1rem + var(--safe-area-inset-top))`}}>
              <Loader className="w-6 h-6 text-white animate-spin" />
          </div>
      )}
      <div
          className="fixed top-0 left-0 right-0 z-40 transition-transform duration-300"
          style={{ transform: `translateY(${Math.min(pullDistance, 80)}px)` }}
      >
        <header className="relative backdrop-blur-xl bg-black/50 border-b border-white/10" style={{ paddingTop: 'var(--safe-area-inset-top)' }}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-20">
              <div className="flex items-center gap-8">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 blur-lg animate-pulse" />
                    <div className="relative bg-gradient-to-r from-purple-600 to-pink-600 p-2 rounded-xl">
                      <Sparkles className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <div>
                    <h1 className="text-2xl font-black bg-gradient-to-r from-purple-400 to-pink-400 text-transparent bg-clip-text">AI Sim</h1>
                  </div>
                </div>
                
                <div className="hidden lg:flex items-center gap-6 px-6 py-3 bg-white/5 rounded-2xl backdrop-blur-xl border border-white/10">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 bg-gradient-to-r ${rankColors[currentRank.color]} rounded-lg`}>
                      {currentRank.icon}
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">Rank</p>
                      <p className="text-sm font-bold text-white">{currentRank.name}</p>
                    </div>
                  </div>
                  
                  <div className="w-px h-10 bg-white/20" />
                  
                  <div className="flex items-center gap-3">
                    <div className="w-32">
                      <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                        <span>Level {user.level}</span>
                        <span>Level {user.level + 1}</span>
                      </div>
                      <AnimatedProgressBar value={user.xp} max={user.nextLevelXp} color="rainbow" height="h-3" showLabel={true} glowing={true} />
                    </div>
                  </div>
                  
                  <div className="w-px h-10 bg-white/20" />
                  
                  <div className="flex items-center gap-2">
                    <Flame className="w-5 h-5 text-orange-400" />
                    <span className="text-white font-bold">{user.dailyStreak}</span>
                    <span className="text-xs text-gray-400">day streak</span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2 sm:gap-4">
                <div className="relative">
                  <button onClick={handleNotificationsToggle} className="relative p-3 text-gray-400 hover:text-white transition-colors">
                    <Bell className="w-5 h-5" />
                    {hasNewNotifications && <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />}
                  </button>
                  {activeDropdown === 'notifications' && (
                    <div className="absolute right-0 mt-2 w-screen max-w-sm sm:w-72 bg-black/70 backdrop-blur-xl border border-white/10 rounded-xl shadow-lg z-50 animate-fadeIn">
                      <div className="p-3">
                        <div className="flex justify-between items-center mb-2">
                            <h4 className="font-bold text-white">Notifications</h4>
                            <span className="text-xs text-purple-400 cursor-pointer hover:underline">Mark all as read</span>
                        </div>
                        <div className="space-y-2">
                            <div className="p-2 bg-white/5 rounded-md text-sm text-gray-300">
                                <p>🎉 <span className="font-semibold">Welcome to AI Sim!</span> Explore the tools to level up.</p>
                            </div>
                            <div className="p-2 bg-white/5 rounded-md text-sm text-gray-300">
                                <p>🎯 Your daily quests have been refreshed. Check them out!</p>
                            </div>
                            <div className="p-2 bg-white/5 rounded-md text-sm text-gray-300">
                                <p>✨ You earned the 'First Steps' achievement! Keep going.</p>
                            </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                <button onClick={() => { onOpenStore(); triggerHapticFeedback(); }} className="flex items-center gap-2 px-3 py-2 sm:px-4 sm:py-2 bg-gradient-to-r from-yellow-600/20 to-orange-600/20 backdrop-blur-xl rounded-xl border border-yellow-500/30 hover:shadow-lg hover:shadow-yellow-500/20 transition-all">
                  <ShoppingCart className="w-4 h-4 text-yellow-400" />
                  <span className="font-bold text-yellow-400">{user.credits}</span>
                </button>
                
                <div className="relative">
                  <div onClick={handleUserMenuToggle} className="relative group">
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full blur-md opacity-50 group-hover:opacity-100 transition-opacity" />
                    <div className="relative w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center cursor-pointer overflow-hidden">
                       {user.photoUrl ? (
                         <img src={user.photoUrl} alt="Profile" className="w-full h-full object-cover" />
                       ) : (
                         <span className="text-white font-bold text-lg">{user.name?.[0]}</span>
                       )}
                    </div>
                  </div>
                  {activeDropdown === 'user' && (
                    <div className="absolute right-0 mt-2 w-screen max-w-xs sm:w-48 bg-black/70 backdrop-blur-xl border border-white/10 rounded-xl shadow-lg z-50 animate-fadeIn">
                      <div className="p-2">
                        <button onClick={() => { onOpenProfile(); setActiveDropdown(null); triggerHapticFeedback(); }} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-white/5 rounded-md flex items-center gap-2"><UserIcon className="w-4 h-4" /> Profile</button>
                        <button onClick={() => { onLogout(); triggerHapticFeedback(); }} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-white/5 rounded-md flex items-center gap-2"><LogOut className="w-4 h-4" /> Logout</button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </header>
      </div>

      <main 
        className="relative z-30 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 transition-transform duration-300"
        style={{ transform: `translateY(${Math.min(pullDistance, 80)}px)` }}
      >
        <div className="pt-20" style={{ paddingTop: '5rem' }}>
          <div className="flex flex-col gap-8">

            {/* Quests, Courses, and Achievements section */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 backdrop-blur-xl rounded-2xl border border-purple-500/20 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Target className="w-5 h-5 text-purple-400" />
                    Daily Quests
                  </h3>
                  <span className="text-xs text-gray-400">Resets in 14h</span>
                </div>
                
                <div className="space-y-3">
                  {activeQuests.map(quest => (
                    <div key={quest.id} className="bg-black/30 rounded-xl p-3 border border-white/5 hover:border-purple-500/30 transition-all">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-white">{quest.title}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-yellow-400">+{quest.xpReward} XP</span>
                          <span className="text-xs text-cyan-400">+{quest.creditReward} 💎</span>
                        </div>
                      </div>
                      <p className="text-xs text-gray-400 mb-2">{quest.description}</p>
                      <AnimatedProgressBar value={quest.progress} max={quest.total} color="purple" height="h-1.5" />
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-indigo-900/30 to-blue-900/30 backdrop-blur-xl rounded-2xl border border-indigo-500/20 p-6">
                  <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-white flex items-center gap-2">
                          <GraduationCap className="w-5 h-5 text-indigo-400" />
                          My Courses
                      </h3>
                      <button onClick={() => { onCreateCourse(); triggerHapticFeedback(); }} className="px-3 py-1 text-xs font-semibold bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors">Create New</button>
                  </div>
                  <div className="space-y-3">
                      {(user.customCourses && user.customCourses.length > 0) ? user.customCourses.map(course => (
                          <div key={course.id} className="bg-black/30 rounded-xl p-3 border border-white/5 hover:border-indigo-500/30 transition-all">
                              <div className="flex items-center justify-between">
                                  <span className="text-sm font-medium text-white truncate pr-2">{course.title}</span>
                                  <div className="flex items-center gap-2 flex-shrink-0">
                                    <button onClick={() => { onEditCourse(course); triggerHapticFeedback(); }} className="p-2 text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-md transition-colors"><Edit3 className="w-4 h-4" /></button>
                                    <button onClick={() => { onPlayCourse(course); triggerHapticFeedback(); }} className="p-2 text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-md transition-colors"><Play className="w-4 h-4" /></button>
                                  </div>
                              </div>
                              <p className="text-xs text-gray-400 mt-2">
                                {course.userProgress?.completed ? 'Completed' : `In Progress: Module ${ (course.userProgress?.currentModuleIndex || 0) + 1} / ${course.modules.length}`}
                              </p>
                          </div>
                      )) : (
                          <div className="text-center py-4">
                              <p className="text-sm text-gray-400">No courses yet.</p>
                              <p className="text-xs text-gray-500">Create a course to start a personalized quiz!</p>
                          </div>
                      )}
                  </div>
              </div>

              <div className="md:col-span-2 lg:col-span-1 bg-gradient-to-br from-green-900/30 to-emerald-900/30 backdrop-blur-xl rounded-2xl border border-green-500/20 p-6">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                    <Medal className="w-5 h-5 text-green-400" />
                    Recent Achievements
                  </h3>
                  <div className="space-y-3">
                    {[
                      { name: 'First Steps', desc: 'Use your first tool', icon: <Footprints className="w-4 h-4" />, rarity: 'Common' },
                      { name: 'Essay Master', desc: 'Write 10 essays', icon: <Edit3 className="w-4 h-4" />, rarity: 'Rare' },
                      { name: 'Week Warrior', desc: '7 day streak', icon: <Flame className="w-4 h-4" />, rarity: 'Epic' },
                    ].map((achievement, idx) => (
                      <div key={idx} className="flex items-center gap-3 p-3 bg-black/30 rounded-xl border border-white/5">
                        <div className={`p-2 rounded-lg ${
                          achievement.rarity === 'Common' ? 'bg-gray-600/30 text-gray-400' :
                          achievement.rarity === 'Rare' ? 'bg-blue-600/30 text-blue-400' :
                          'bg-purple-600/30 text-purple-400'
                        }`}>
                          {achievement.icon}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-white">{achievement.name}</p>
                          <p className="text-xs text-gray-400">{achievement.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
              </div>
            </div>

            {/* Tools Section */}
            <div>
              <div className="mb-4">
                  <h3 className="text-lg font-bold text-white mb-3">Tool Categories</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2">
                      {toolCategories.map((category) => (
                          <button
                              key={category}
                              onClick={() => { setActiveCategory(category); triggerHapticFeedback(); }}
                              className={`w-full py-2.5 px-3 rounded-xl font-medium transition-all text-sm ${
                                  category === activeCategory 
                                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/30' 
                                      : 'text-gray-400 bg-white/5 hover:text-white hover:bg-white/10'
                              }`}
                          >
                              {category}
                          </button>
                      ))}
                  </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredTools.map((tool) => (
                    <div
                      key={tool.id}
                      onClick={() => { onSelectTool(tool); triggerHapticFeedback(); }}
                      className="group relative overflow-hidden rounded-2xl cursor-pointer"
                    >
                      <div className={`absolute inset-0 bg-gradient-to-br ${tool.gradient} opacity-10 group-hover:opacity-20 transition-opacity duration-500`} />
                      <div className="relative bg-black/40 backdrop-blur-xl p-6 border border-white/10 hover:border-white/20 transition-all duration-300 h-full flex flex-col">
                        <div className="flex items-start justify-between mb-3">
                          <div className={`p-2.5 bg-gradient-to-br ${tool.gradient} rounded-xl text-white`}>
                            {tool.icon}
                          </div>
                          <div className="flex flex-col items-end gap-1">
                            <span className={`px-2 py-0.5 text-xs font-bold rounded-full ${
                              tool.difficulty === 'Easy' ? 'bg-green-500/20 text-green-400' :
                              tool.difficulty === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                              tool.difficulty === 'Hard' ? 'bg-orange-500/20 text-orange-400' :
                              'bg-red-500/20 text-red-400'
                            }`}>
                              {tool.difficulty}
                            </span>
                            <span className="text-xs text-purple-400 font-medium">+{tool.xpReward} XP</span>
                          </div>
                        </div>
                        <h3 className="text-white font-bold mb-1">{tool.name}</h3>
                        <p className="text-xs text-gray-400 mb-3 line-clamp-2 flex-grow">{tool.description}</p>
                        <div className="flex items-center justify-between mt-auto pt-3">
                          <div className="flex items-center gap-2">
                            {(toolStats[tool.id]?.streak || 0) > 0 && (
                              <div className="flex items-center gap-1 px-2 py-1 bg-orange-500/20 rounded-lg">
                                <Flame className="w-3 h-3 text-orange-400" />
                                <span className="text-xs text-orange-400 font-bold">{toolStats[tool.id].streak}</span>
                              </div>
                            )}
                            <span className="text-xs text-gray-500">Used {toolStats[tool.id]?.usage || 0}x</span>
                          </div>
                          <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-white group-hover:translate-x-1 transition-all" />
                        </div>
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/0 via-purple-600/0 to-purple-600/0 group-hover:from-purple-600/10 group-hover:via-pink-600/10 group-hover:to-cyan-600/10 transition-all duration-500 rounded-2xl pointer-events-none" />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;```

---

## components/ToolPage.tsx

```typescript
import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI } from '@google/genai';
import { UserProfile, Tool, ChatMessage, Course, Module, AttachedFile } from '../types.ts';
import { ArrowLeft, Send, AILoader, Sparkles, AlertTriangle, User as UserIcon, Copy, Check, ThumbsUp, ThumbsDown, GoogleDrive, Loader, Paperclip, File as FileIcon, X, ChevronRight } from './icons.tsx';
import ParticleEffect from './ParticleEffect.tsx';
import { ALL_TOOLS } from '../constants.tsx';
import VoiceInputButton from './VoiceInputButton.tsx';
import AudioPlayer from './AudioPlayer.tsx';
import { fileToBase64, readFileAsText } from '../utils/fileUtils.ts';
import { triggerHapticFeedback } from '../utils/mobileUtils.ts';

interface ToolPageProps {
  user: UserProfile | null;
  selectedTool: Tool;
  chatHistories: { [key: string]: ChatMessage[] };
  onNavigate: (page: 'dashboard') => void;
  onUseTool: (toolId: string, xpReward: number, userPrompt: string, modelResponse: string) => void;
  onSetSatisfaction: (toolId: string, messageIndex: number, satisfaction: 'satisfied' | 'unsatisfied') => void;
  onGiveFeedback: (xp: number) => void;
  courseContext?: Course | null;
  onUpdateCourseProgress?: (courseId: string, progress: { correct: number, total: number, lastScore: number }) => void;
}

const FormattedResponse: React.FC<{ text: string }> = ({ text }) => {
  const codeBlockRegex = /```([\s\S]*?)```/g;
  const parts = text.split(codeBlockRegex);

  return (
    <div>
      {parts.map((part, index) => {
        // This is a code block
        if (index % 2 === 1) {
          const codeContent = part.split('\n').slice(1).join('\n'); // remove language hint
          return (
            <pre key={index} className="bg-black/50 p-3 rounded-md font-mono text-sm my-2 block overflow-x-auto">
              <code>{codeContent || part}</code>
            </pre>
          );
        }

        // This is regular text, process it further
        const boldRegex = /\*\*(.*?)\*\*/g;
        return part.split('\n').map((line, lineIndex) => {
          if (line.trim() === '') return null;

          // Headings
          if (line.startsWith('# ')) {
            const content = line.substring(2);
            return <h1 key={`${index}-${lineIndex}`} className="text-lg sm:text-xl font-bold my-3 pt-2">{content}</h1>;
          }
          if (line.startsWith('## ')) {
            const content = line.substring(3);
            return <h2 key={`${index}-${lineIndex}`} className="text-base sm:text-lg font-semibold my-2 pt-1">{content}</h2>;
          }

          // Handle list items with a new, styled block for separation
          const trimmedLine = line.trim();
          if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ')) {
            const content = trimmedLine.substring(trimmedLine.indexOf(' ') + 1);
            const formattedContent = content.split(boldRegex).map((subPart, i) =>
              i % 2 === 1 ? <strong key={i} className="font-bold text-white">{subPart}</strong> : subPart
            );
            return (
              <div key={`${index}-${lineIndex}`} className="flex items-start gap-3 my-3 p-4 bg-black/20 border-l-4 border-purple-500 rounded-r-lg">
                <Check className="w-5 h-5 text-purple-400 mt-1 flex-shrink-0" />
                <div className="flex-grow text-gray-200">{formattedContent}</div>
              </div>
            );
          }

          // Handle paragraphs with bold text
          const formattedLine = line.split(boldRegex).map((subPart, i) =>
            i % 2 === 1 ? <strong key={i} className="font-bold text-white">{subPart}</strong> : subPart
          );
          return <p key={`${index}-${lineIndex}`} className="my-2">{formattedLine}</p>;
        }).filter(Boolean);
      })}
    </div>
  );
};


const ToolPage: React.FC<ToolPageProps> = ({ user, selectedTool, chatHistories, onNavigate, onUseTool, onSetSatisfaction, onGiveFeedback, courseContext, onUpdateCourseProgress }) => {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedResponse, setCopiedResponse] = useState<number | null>(null);
  const [longPressCopied, setLongPressCopied] = useState<number | null>(null);
  const [savingToDrive, setSavingToDrive] = useState<number | null>(null);
  const [savedToDrive, setSavedToDrive] = useState<number | null>(null);
  const [promptExamples, setPromptExamples] = useState<string[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [attachedFile, setAttachedFile] = useState<AttachedFile | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const longPressTimer = useRef<number | null>(null);
  
  const currentChatHistory = chatHistories[selectedTool.id] || [];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentChatHistory, isLoading]);
  
  useEffect(() => {
    if (selectedTool.promptExamples) {
      if (typeof selectedTool.promptExamples === 'function') {
        setPromptExamples(selectedTool.promptExamples(user));
      } else {
        setPromptExamples(selectedTool.promptExamples);
      }
    } else {
      setPromptExamples([]);
    }
    setPrompt('');
  }, [selectedTool, user]);

  const handleGenerate = async (initialPrompt?: string) => {
    const promptToSend = initialPrompt || prompt;
    if ((!promptToSend.trim() && !attachedFile) || isLoading || !user) return;


    setIsLoading(true);
    setError(null);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

      const userContext = `
[START USER CONTEXT]
The user is a ${user.academicYear} student at ${user.university} majoring in ${user.major}.
Their primary goals are: ${user.goals.join(', ')}.
[END USER CONTEXT]
`;

      const otherToolHistories = (Object.entries(chatHistories) as [string, ChatMessage[]][])
        .filter(([toolId, history]) => toolId !== selectedTool.id && history.length > 0)
        .map(([toolId, history]) => ({
          toolId,
          lastMessageTimestamp: new Date(history[history.length - 1].timestamp || 0).getTime(),
          history,
        }))
        .sort((a, b) => b.lastMessageTimestamp - a.lastMessageTimestamp)
        .slice(0, 2);

      let sharedContext = `
[START SHARED CONTEXT]
`;
      if (otherToolHistories.length > 0) {
        sharedContext += "Recent activity in other tools (use this for context):\n";
        otherToolHistories.forEach(({ toolId, history }) => {
          const toolName = ALL_TOOLS.find(t => t.id === toolId)?.name || toolId;
          const lastUserPrompt = history.filter(m => m.role === 'user').pop()?.text;
          const lastModelResponse = history.filter(m => m.role === 'model').pop()?.text;
          
          if(lastUserPrompt && lastModelResponse) {
              sharedContext += `- In '${toolName}': The user last asked "${lastUserPrompt.substring(0, 100)}..." and you responded "${lastModelResponse.substring(0, 150)}...".\n`;
          }
        });
      }
      sharedContext += "[END SHARED CONTEXT]\n\n";

      let personalizedSystemInstruction = `${userContext}\n${sharedContext}\n${selectedTool.systemInstruction || ''}`;
      
      const parts: any[] = [];
      let userPromptForHistory = promptToSend;

      if (promptToSend) {
        parts.push({ text: promptToSend });
      }

      if (attachedFile) {
        if (attachedFile.type.startsWith('image/')) {
          parts.push({
            inlineData: {
              mimeType: attachedFile.type,
              data: attachedFile.data,
            },
          });
        } else if (attachedFile.type.startsWith('text/')) {
          const fileContentForPrompt = `\n\n--- Attached File: ${attachedFile.name} ---\n${attachedFile.data}`;
          if (parts.length > 0 && parts[0].text) {
             parts[0].text += fileContentForPrompt;
          } else {
             parts.unshift({ text: fileContentForPrompt });
          }
          userPromptForHistory += ` [Attached: ${attachedFile.name}]`;
        }
      }
      
      const contents = [
        ...currentChatHistory.map(msg => ({
          role: msg.role,
          parts: [{ text: msg.text }]
        })),
        { role: 'user' as const, parts: parts }
      ];

      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: contents,
        ...(personalizedSystemInstruction && {
          config: { systemInstruction: personalizedSystemInstruction }
        })
      });

      const responseText = response.text;
      onUseTool(selectedTool.id, selectedTool.xpReward, userPromptForHistory, responseText);
      if (!initialPrompt) {
        setPrompt('');
      }
    } catch (e: any) {
      console.error('Gemini API Error:', e);
      setError(e.message || 'An error occurred while generating the response.');
    } finally {
      setIsLoading(false);
      setAttachedFile(null);
    }
  };

  const moduleToText = (module: Module): string => {
    let content = `Title: ${module.title}\n\nIntroduction: ${module.introduction}\n\n`;
    content += "Key Concepts:\n";
    module.keyConcepts.forEach(kc => {
      content += `- ${kc.title}: ${kc.explanation}\n`;
    });
    content += "\nPractical Examples:\n";
    module.practicalExamples.forEach(pe => {
      content += `- ${pe.title}: ${pe.description}\n`;
    });
    content += `\nSummary: ${module.summary}`;
    return content;
  };

  useEffect(() => {
    if (courseContext && selectedTool.id === 'study-buddy' && currentChatHistory.length === 0) {
      const courseContentForQuiz = courseContext.modules.map(moduleToText).join('\n\n---\n\n');
      const initialPrompt = `Please generate a practice quiz based on the following course material. Ask me one question at a time. Course material: """${courseContentForQuiz}"""`;
      handleGenerate(initialPrompt);
    }
  }, [courseContext, selectedTool.id]);

  const handleFinishQuiz = () => {
      triggerHapticFeedback();
      if (!courseContext || !onUpdateCourseProgress) return;

      let correct = 0;
      const modelResponses = currentChatHistory.filter(m => m.role === 'model' && m.text.toLowerCase().includes('answer is'));
      
      modelResponses.forEach(msg => {
          const text = msg.text.toLowerCase();
          if (text.includes('is correct')) {
              correct++;
          }
      });

      const total = modelResponses.length;
      const lastScore = total > 0 ? Math.round((correct / total) * 100) : 0;

      onUpdateCourseProgress(courseContext.id, { correct, total, lastScore });
      onNavigate('dashboard');
  };

  const handleCopy = (text: string, index: number) => {
    triggerHapticFeedback();
    navigator.clipboard.writeText(text);
    setCopiedResponse(index);
    setTimeout(() => setCopiedResponse(null), 2000);
  };

  const handleSaveToDrive = (text: string, index: number) => {
    triggerHapticFeedback();
    setSavingToDrive(index);
    setSavedToDrive(null);
    setTimeout(() => {
      try {
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `AISim-Response-${new Date().toISOString()}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        setSavedToDrive(index);
      } catch (error) {
        console.error("Failed to save file:", error);
      } finally {
        setSavingToDrive(null);
        setTimeout(() => setSavedToDrive(null), 2000);
      }
    }, 1000);
  };
  
  const handleSetSatisfaction = (toolId: string, messageIndex: number, satisfaction: 'satisfied' | 'unsatisfied') => {
    triggerHapticFeedback();
    const currentHistory = chatHistories[toolId] || [];
    const currentMessage = currentHistory[messageIndex];
    const wasAlreadySatisfied = currentMessage?.satisfaction === 'satisfied';

    onSetSatisfaction(toolId, messageIndex, satisfaction);
    
    if (satisfaction === 'satisfied' && !wasAlreadySatisfied) {
      onGiveFeedback(5);
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleGenerate();
    }
  };
  
  const handleAttachClick = () => {
    triggerHapticFeedback();
    fileInputRef.current?.click();
  };

  const handleRemoveFile = () => {
      triggerHapticFeedback();
      setAttachedFile(null);
      if (fileInputRef.current) {
          fileInputRef.current.value = '';
      }
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      if (file.size > 4 * 1024 * 1024) {
          setError('File is too large. Please select a file smaller than 4MB.');
          event.target.value = '';
          return;
      }

      const supportedImageTypes = ['image/jpeg', 'image/png', 'image/webp'];
      const supportedTextTypes = ['text/plain', 'text/markdown'];

      if (supportedImageTypes.includes(file.type)) {
          try {
              const base64Data = await fileToBase64(file);
              const previewUrl = URL.createObjectURL(file);
              setAttachedFile({ name: file.name, type: file.type, size: file.size, data: base64Data, previewUrl });
          } catch (error) {
              console.error('Error processing image file:', error);
              setError('Could not process the image file.');
          }
      } else if (supportedTextTypes.includes(file.type)) {
          try {
              const textContent = await readFileAsText(file);
              setAttachedFile({ name: file.name, type: file.type, size: file.size, data: textContent });
          } catch (error) {
              console.error('Error reading text file:', error);
              setError('Could not read the text file.');
          }
      } else {
          setError(`Unsupported file type: ${file.type}. Please use images (PNG, JPEG, WEBP) or text files (.txt, .md).`);
      }

      event.target.value = '';
  };

  const handleLongPressStart = (text: string, index: number) => {
    longPressTimer.current = window.setTimeout(() => {
        navigator.clipboard.writeText(text);
        triggerHapticFeedback();
        setLongPressCopied(index);
        setTimeout(() => setLongPressCopied(null), 1500);
    }, 500); // 500ms for long press
  };

  const handleLongPressEnd = () => {
      if(longPressTimer.current) {
          clearTimeout(longPressTimer.current);
          longPressTimer.current = null;
      }
  };


  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      <div className="fixed inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-black to-pink-900/10" />
        <ParticleEffect />
      </div>

      <header className="relative z-40 backdrop-blur-xl bg-black/50 border-b border-white/10 flex-shrink-0" style={{ paddingTop: 'var(--safe-area-inset-top)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center gap-4">
              <button onClick={() => { onNavigate('dashboard'); triggerHapticFeedback(); }} className="p-3 rounded-full hover:bg-white/10 transition-colors">
                <ArrowLeft className="w-6 h-6" />
              </button>
              <div className="flex items-center gap-3">
                <div className={`p-2 bg-gradient-to-br ${selectedTool.gradient} rounded-xl text-white`}>
                  {selectedTool.icon}
                </div>
                <div>
                  <h1 className="text-xl font-bold">{selectedTool.name}</h1>
                  <p className="text-sm text-gray-400">{courseContext ? `Quiz: ${courseContext.title}` : selectedTool.description}</p>
                </div>
              </div>
            </div>
            {courseContext && selectedTool.id === 'study-buddy' && onUpdateCourseProgress && (
              <button onClick={handleFinishQuiz} className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold rounded-xl hover:shadow-lg hover:shadow-green-500/50 transform hover:scale-105 transition-all">
                Finish & Save Progress
              </button>
            )}
          </div>
        </div>
      </header>
      
      <main className="flex-grow flex flex-col relative z-30 overflow-hidden">
        <div className="flex-grow overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6">
          {currentChatHistory.length === 0 && !isLoading && !courseContext &&(
            <div className="text-center p-8 bg-black/30 rounded-2xl border border-white/10 max-w-2xl mx-auto">
              <div className={`w-16 h-16 mx-auto mb-4 bg-gradient-to-br ${selectedTool.gradient} rounded-2xl flex items-center justify-center text-white`}>
                {React.cloneElement(selectedTool.icon as React.ReactElement<any>, { className: "w-8 h-8" })}
              </div>
              <h2 className="text-2xl font-bold mb-2">Welcome to {selectedTool.name}</h2>
              <p className="text-gray-400 mb-4">{promptExamples.length > 0 ? 'Swipe through the examples below or type your own prompt.' : 'Start by typing your request in the box below.'}</p>
              {promptExamples.length > 0 && (
                 <div className="relative -mx-4 sm:-mx-6 lg:-mx-8">
                    <div className="flex gap-2 overflow-x-auto whitespace-nowrap px-4 sm:px-6 lg:px-8 pb-3 hide-scrollbar scroll-mask snap-x snap-mandatory">
                      {promptExamples.map((example, index) => (
                        <button 
                          key={index} 
                          onClick={() => { setPrompt(example); triggerHapticFeedback(); }} 
                          className="flex-shrink-0 text-left px-4 py-3 bg-white/5 text-sm text-gray-300 rounded-lg hover:bg-white/10 transition-colors snap-start max-w-xs truncate"
                        >
                          "{example}"
                        </button>
                      ))}
                    </div>
                  </div>
              )}
            </div>
          )}

          {currentChatHistory.map((message, index) => (
            <div key={index} className={`flex gap-2 sm:gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-2xl w-full flex items-start gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                 <div className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center ${message.role === 'model' ? `bg-gradient-to-br ${selectedTool.gradient}` : 'bg-gray-700'}`}>
                   {message.role === 'model' ? <Sparkles className="w-5 h-5 text-white" /> : <UserIcon className="w-5 h-5 text-white" />}
                 </div>
                 
                 {message.role === 'user' ? (
                   <div className="p-5 rounded-2xl w-full text-gray-200 leading-relaxed bg-purple-600">
                     <p className="whitespace-pre-wrap">{message.text}</p>
                   </div>
                 ) : (
                   <div className={`p-[2px] rounded-2xl w-full bg-gradient-to-br ${selectedTool.gradient} relative`}>
                      {longPressCopied === index && (
                          <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full animate-fadeIn">
                              Copied!
                          </div>
                      )}
                     <div 
                        className="p-5 rounded-[14px] w-full text-gray-200 leading-relaxed bg-black/40 backdrop-blur-md"
                        onTouchStart={() => handleLongPressStart(message.text, index)}
                        onTouchEnd={handleLongPressEnd}
                        onContextMenu={(e) => e.preventDefault()}
                      >
                        <FormattedResponse text={message.text} />
                        <AudioPlayer text={message.text} />
                        <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between">
                           <div className="flex items-center gap-1 sm:gap-3">
                              <button onClick={() => handleCopy(message.text, index)} className="text-gray-400 hover:text-white transition-colors flex items-center gap-1.5 text-xs p-2 sm:p-0">
                                {copiedResponse === index ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                                <span className="hidden sm:inline">{copiedResponse === index ? 'Copied!' : 'Copy'}</span>
                              </button>
                              <button 
                                onClick={() => handleSaveToDrive(message.text, index)} 
                                className="text-gray-400 hover:text-white transition-colors flex items-center gap-1.5 text-xs p-2 sm:p-0 disabled:opacity-50"
                                disabled={savingToDrive === index || savedToDrive === index}
                              >
                                {savingToDrive === index ? (
                                    <><Loader className="w-4 h-4 animate-spin" /> <span className="hidden sm:inline">Saving...</span></>
                                ) : savedToDrive === index ? (
                                    <><Check className="w-4 h-4 text-green-400" /> <span className="hidden sm:inline">Saved!</span></>
                                ) : (
                                    <><GoogleDrive className="w-4 h-4" /> <span className="hidden sm:inline">Save</span></>
                                )}
                              </button>
                           </div>
                           <div className="flex items-center gap-1">
                             <button onClick={() => handleSetSatisfaction(selectedTool.id, index, 'satisfied')} className={`p-2 rounded-md ${message.satisfaction === 'satisfied' ? 'bg-green-500/20 text-green-400' : 'text-gray-400 hover:text-green-400 hover:bg-green-500/10'}`}>
                               <ThumbsUp className="w-5 h-5"/>
                             </button>
                              <button onClick={() => handleSetSatisfaction(selectedTool.id, index, 'unsatisfied')} className={`p-2 rounded-md ${message.satisfaction === 'unsatisfied' ? 'bg-red-500/20 text-red-400' : 'text-gray-400 hover:text-red-400 hover:bg-red-500/10'}`}>
                               <ThumbsDown className="w-5 h-5"/>
                             </button>
                           </div>
                        </div>
                     </div>
                   </div>
                 )}
               </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start gap-4">
               <div className="max-w-2xl w-full flex items-start gap-3">
                 <div className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center bg-gradient-to-br ${selectedTool.gradient}`}>
                   <Sparkles className="w-5 h-5 text-white" />
                 </div>
                 <div className="p-4 rounded-2xl bg-gray-800/80 backdrop-blur-sm flex items-center gap-3">
                   <AILoader className="w-6 h-6 text-purple-400" />
                   <span className="font-semibold text-purple-300">AISim in Action...</span>
                 </div>
               </div>
            </div>
          )}
          
          {error && (
            <div className="bg-red-500/20 border border-red-500 text-red-300 p-4 rounded-lg flex items-center gap-3 max-w-2xl mx-auto">
              <AlertTriangle className="w-5 h-5" />
              <div>
                <p className="font-bold">An error occurred</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        <div className="flex-shrink-0 bg-black/50 backdrop-blur-xl border-t border-white/10" style={{ paddingBottom: 'var(--safe-area-inset-bottom)'}}>
          <div className="p-4 sm:p-6 lg:p-8 pt-4 max-w-3xl mx-auto">
            {attachedFile && (
                <div className="mb-3 p-2 bg-gray-800 rounded-lg flex items-center justify-between animate-fadeIn border border-white/10">
                    <div className="flex items-center gap-3 overflow-hidden">
                        {attachedFile.previewUrl ? (
                            <img src={attachedFile.previewUrl} alt={attachedFile.name} className="w-10 h-10 rounded object-cover flex-shrink-0" />
                        ) : (
                            <div className="w-10 h-10 flex items-center justify-center bg-gray-700 rounded flex-shrink-0">
                                <FileIcon className="w-6 h-6 text-gray-400" />
                            </div>
                        )}
                        <div className="overflow-hidden">
                            <p className="text-sm font-medium text-white truncate">{attachedFile.name}</p>
                            <p className="text-xs text-gray-400">{(attachedFile.size / 1024).toFixed(2)} KB</p>
                        </div>
                    </div>
                    <button onClick={handleRemoveFile} className="p-2 rounded-full text-gray-400 hover:bg-gray-700 hover:text-white flex-shrink-0">
                        <X className="w-5 h-5" />
                    </button>
                </div>
            )}
            <div className="relative">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                accept="image/png, image/jpeg, image/webp, text/plain, text/markdown"
              />
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={attachedFile ? `Describe the file or ask a question...` : `Type your prompt for ${selectedTool.name}... (Shift+Enter for new line)`}
                className="w-full bg-gray-900 border border-gray-700 rounded-2xl py-4 pl-14 pr-28 sm:pr-32 text-white placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all resize-none"
                rows={1}
                style={{ minHeight: '56px', maxHeight: '200px' }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = `${target.scrollHeight}px`;
                }}
              />
              <div className="absolute left-3 top-1/2 -translate-y-1/2">
                <button
                  onClick={handleAttachClick}
                  className="p-3 rounded-full text-gray-400 hover:bg-gray-700 hover:text-white transition-colors"
                  aria-label="Attach file"
                >
                  <Paperclip className="w-5 h-5" />
                </button>
              </div>
              <div className="absolute right-16 sm:right-20 top-1/2 -translate-y-1/2">
                <VoiceInputButton
                  onTranscriptChange={(transcript) => setPrompt(prev => prev + transcript)}
                  isListening={isListening}
                  setIsListening={setIsListening}
                />
              </div>
              <button
                onClick={() => { handleGenerate(); triggerHapticFeedback(); }}
                disabled={isLoading || (!prompt.trim() && !attachedFile)}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-3 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-purple-500/50 transform hover:scale-105 transition-all"
              >
                {isLoading ? <AILoader className="w-5 h-5 text-white" /> : <Send className="w-5 h-5" />}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2 text-center">
              AI Sim can make mistakes. Consider checking important information.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ToolPage;```

---

## components/LandingPage.tsx

```typescript
import React from 'react';
import FloatingOrb from './FloatingOrb.tsx';
import ParticleEffect from './ParticleEffect.tsx';
import { Sparkles } from './icons.tsx';

interface LandingPageProps {
  onNavigateToPricing: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onNavigateToPricing }) => {
  return (
    <div className="min-h-screen bg-black text-white relative overflow-x-hidden">
      <div className="fixed inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-black to-pink-900/10" />
        <ParticleEffect />
        <FloatingOrb color="purple" />
        <FloatingOrb color="blue" delay={2} />
        <FloatingOrb color="green" delay={4} />
      </div>

      <div className="relative z-10">
        <section className="min-h-screen flex flex-col items-center justify-center text-center p-4">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="relative">
              <div className="absolute -inset-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur-lg animate-pulse" />
              <div className="relative bg-gradient-to-r from-purple-600 to-pink-600 p-3 rounded-2xl">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
            </div>
            <h1 className="text-5xl lg:text-6xl font-black bg-gradient-to-r from-purple-400 to-pink-400 text-transparent bg-clip-text">
              AI Sim
            </h1>
          </div>
          <p className="text-lg md:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Your personal AI-powered mentor for academic excellence, career preparation, and personal wellness.
          </p>
          <button
            onClick={onNavigateToPricing}
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-lg rounded-xl hover:shadow-2xl hover:shadow-purple-500/50 transform hover:scale-105 transition-all duration-200"
          >
            Begin Your Journey
          </button>
        </section>
        
      </div>
    </div>
  );
};

export default LandingPage;
```

---

## vite.config.ts

```typescript
import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [react()],
      define: {
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      },
      build: {
        rollupOptions: {
          output: {
            manualChunks: {
              'react-vendor': ['react', 'react-dom'],
              'ai-vendor': ['@google/genai'],
              'icons': ['./components/icons.tsx'],
            },
          },
        },
        chunkSizeWarningLimit: 1000,
        minify: 'esbuild',
        sourcemap: false,
      },
      optimizeDeps: {
        include: ['react', 'react-dom', '@google/genai'],
      },
    };
});
```

## package.json

```json
{
  "name": "final-ai-sim",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.1.1",
    "react-dom": "^19.1.1",
    "@google/genai": "latest"
  },
  "devDependencies": {
    "@types/node": "^22.14.0",
    "@vitejs/plugin-react": "^5.0.0",
    "typescript": "~5.8.2",
    "vite": "^6.2.0"
  }
}
```

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "experimentalDecorators": true,
    "useDefineForClassFields": false,
    "module": "ESNext",
    "lib": [
      "ES2022",
      "DOM",
      "DOM.Iterable"
    ],
    "skipLibCheck": true,
    "types": [
      "node"
    ],
    "moduleResolution": "bundler",
    "isolatedModules": true,
    "moduleDetection": "force",
    "allowJs": true,
    "jsx": "react-jsx",
    "paths": {
      "@/*": [
        "./*"
      ]
    },
    "allowImportingTsExtensions": true,
    "noEmit": true
  }
}```

