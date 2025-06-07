import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowRight, Bot, Target, Share2 } from 'lucide-react';
import { Terminal } from './terminal';

export default function HomePage() {
  return (
    <main>
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-12 lg:gap-8">
            <div className="sm:text-center md:max-w-2xl md:mx-auto lg:col-span-6 lg:text-left">
              <h1 className="text-4xl font-bold text-gray-900 tracking-tight sm:text-5xl md:text-6xl">
                Automate Your Job Advertising
                <span className="block text-orange-500">with AdFlux</span>
              </h1>
              <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-xl lg:text-lg xl:text-xl">
                Stop wasting time and money. AdFlux automatically posts your job ads to Meta, Google, and X, reaching the best candidates with AI-powered targeting.
              </p>
              <div className="mt-8 sm:max-w-lg sm:mx-auto sm:text-center lg:text-left lg:mx-0">
                <Link href="/dashboard/jobs/create">
                  <Button
                    size="lg"
                    className="text-lg rounded-full bg-orange-500 hover:bg-orange-600 text-white"
                  >
                    Create Your First Ad
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
              </div>
            </div>
            <div className="mt-12 relative sm:max-w-lg sm:mx-auto lg:mt-0 lg:max-w-none lg:mx-0 lg:col-span-6 lg:flex lg:items-center">
              <Terminal />
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-3 lg:gap-8">
            <div className="mt-10 lg:mt-0">
              <div className="flex items-center justify-center h-12 w-12 rounded-md bg-orange-500 text-white">
                <Bot className="h-6 w-6" />
              </div>
              <div className="mt-5">
                <h2 className="text-lg font-medium text-gray-900">
                  AI-Powered Audience Targeting
                </h2>
                <p className="mt-2 text-base text-gray-500">
                  Our engine analyzes your job description to automatically identify and target the perfect audience for your role.
                </p>
              </div>
            </div>

            <div className="mt-10 lg:mt-0">
              <div className="flex items-center justify-center h-12 w-12 rounded-md bg-orange-500 text-white">
                <Share2 className="h-6 w-6" />
              </div>
              <div className="mt-5">
                <h2 className="text-lg font-medium text-gray-900">
                  Multi-Platform Publishing
                </h2>
                <p className="mt-2 text-base text-gray-500">
                  Connect your accounts once and publish your ads across Meta (Facebook/Instagram), Google Ads, and X simultaneously.
                </p>
              </div>
            </div>

            <div className="mt-10 lg:mt-0">
              <div className="flex items-center justify-center h-12 w-12 rounded-md bg-orange-500 text-white">
                <Target className="h-6 w-6" />
              </div>
              <div className="mt-5">
                <h2 className="text-lg font-medium text-gray-900">
                  Automated Campaign Management
                </h2>
                <p className="mt-2 text-base text-gray-500">
                  AdFlux handles the campaign creation, budget allocation, and scheduling, so you can focus on hiring.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
                Ready to find the best talent?
              </h2>
              <p className="mt-3 max-w-3xl text-lg text-gray-500">
                Stop posting manually. Let AdFlux build and run your job ad campaigns automatically, saving you time and improving your reach.
              </p>
            </div>
            <div className="mt-8 lg:mt-0 flex justify-center lg:justify-end">
              <Link href="/dashboard/jobs/create">
                <Button
                  size="lg"
                  variant="outline"
                  className="text-lg rounded-full"
                >
                  Start Automating Now
                  <ArrowRight className="ml-3 h-6 w-6" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
