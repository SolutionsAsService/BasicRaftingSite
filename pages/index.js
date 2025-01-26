import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function RioGrandeRafting() {
  return (
    <div className="min-h-screen bg-blue-100 flex flex-col items-center p-4">
      <header className="text-center my-6">
        <h1 className="text-4xl font-bold text-blue-800">Rio Grande Rafting Adventures</h1>
        <p className="text-lg text-gray-700">Experience the thrill of the Rio Grande River!</p>
        <nav className="flex justify-center gap-4 mt-6">
          <Link href="/booking">
            <a className="text-blue-600 hover:underline">Book Now</a>
          </Link>
          <Link href="/guides">
            <a className="text-blue-600 hover:underline">Meet Our Guides</a>
          </Link>
          <Link href="/safety">
            <a className="text-blue-600 hover:underline">Safety Info</a>
          </Link>
        </nav>
      </header>

      <main className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="bg-white shadow-md rounded-xl">
          <CardContent className="p-4">
            <h2 className="text-2xl font-semibold text-blue-700">Book Your Adventure</h2>
            <p className="text-gray-600 my-2">
              Select your rafting trip and reserve your spot today.
            </p>
            <Link href="/booking">
              <Button className="bg-blue-600 text-white w-full hover:bg-blue-500">
                Book Now
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="bg-white shadow-md rounded-xl">
          <CardContent className="p-4">
            <h2 className="text-2xl font-semibold text-blue-700">Meet Our Guides</h2>
            <p className="text-gray-600 my-2">
              Learn more about our experienced rafting guides.
            </p>
            <Link href="/guides">
              <Button className="bg-blue-600 text-white w-full hover:bg-blue-500">
                View Guides
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="bg-white shadow-md rounded-xl">
          <CardContent className="p-4">
            <h2 className="text-2xl font-semibold text-blue-700">Safety Information</h2>
            <p className="text-gray-600 my-2">
              Read about our safety measures and what to expect.
            </p>
            <Link href="/safety">
              <Button className="bg-blue-600 text-white w-full hover:bg-blue-500">
                Learn More
              </Button>
            </Link>
          </CardContent>
        </Card>
      </main>

      <footer className="mt-8 text-gray-700 text-center">
        <p>© 2025 Rio Grande Rafting Adventures. All Rights Reserved.</p>
        <p>Contact us: <a href="mailto:info@riogranderafting.com" className="text-blue-600">info@riogranderafting.com</a></p>
      </footer>
    </div>
  );
}
