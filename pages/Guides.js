export default function Guides() {
    return (
      <div className="min-h-screen p-4 bg-blue-100">
        <h1 className="text-3xl font-bold text-center">Meet Our Guides</h1>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 mt-6">
          
          {/* Guide 1 */}
          <div className="bg-white p-4 shadow-md rounded-xl">
            <h2 className="text-xl font-semibold">Guide Name: Jack "Thunder" Thompson</h2>
            <p className="text-gray-600">Years of Experience: 12</p>
            <p className="text-gray-600">Favorite Rapids: Thunderbolt</p>
            <p className="text-gray-500">Jack is known for his calm demeanor in the toughest rapids. With over 12 years of experience, he’s seen it all – from gentle flows to the wildest whitewater.</p>
          </div>
  
          {/* Guide 2 */}
          <div className="bg-white p-4 shadow-md rounded-xl">
            <h2 className="text-xl font-semibold">Guide Name: Emma "Rapid" Carter</h2>
            <p className="text-gray-600">Years of Experience: 8</p>
            <p className="text-gray-600">Favorite Rapids: Cascade Falls</p>
            <p className="text-gray-500">Emma has been guiding for 8 years and is known for her quick thinking and high energy. She loves navigating through the intense Cascade Falls rapids.</p>
          </div>
  
        </div>
      </div>
    );
  }
  
