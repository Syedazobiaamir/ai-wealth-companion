'use client';

import {
  Navbar,
  HeroSection,
  StatsBar,
  FeatureShowcase,
  BenefitsSection,
  ProductPreview,
  CTASection,
  Footer,
} from '@/components/landing';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/30 to-blue-50/30 dark:from-gray-950 dark:via-purple-950/10 dark:to-blue-950/10 overflow-hidden">
      {/* Fixed Navigation */}
      <Navbar />

      {/* Hero Section with Floating Visuals */}
      <HeroSection />

      {/* Social Proof Stats Bar */}
      <StatsBar />

      {/* Feature Showcase with Animated Glass Cards */}
      <FeatureShowcase />

      {/* Why This Platform - Benefits Storytelling */}
      <BenefitsSection />

      {/* Live Product Preview Strip */}
      <ProductPreview />

      {/* Strong Final CTA Section */}
      <CTASection />

      {/* Premium Footer */}
      <Footer />

      {/* Global Styles */}
      <style jsx global>{`
        @keyframes gradient {
          0%, 100% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
        }
        .animate-gradient {
          animation: gradient 3s ease infinite;
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
          width: 10px;
        }
        ::-webkit-scrollbar-track {
          background: transparent;
        }
        ::-webkit-scrollbar-thumb {
          background: linear-gradient(to bottom, #9333ea, #3b82f6);
          border-radius: 5px;
        }
        ::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(to bottom, #7c22ce, #2563eb);
        }

        /* Smooth scrolling */
        html {
          scroll-behavior: smooth;
        }
      `}</style>
    </div>
  );
}
