export default function Booking() {
    return (
      <div className="min-h-screen p-4 bg-blue-100">
        <h1 className="text-3xl font-bold text-center">Book Your Adventure</h1>
        <form className="max-w-lg mx-auto bg-white p-4 rounded-xl shadow-md mt-6">
          <label className="block mb-2 font-semibold text-gray-700">Trip Date:</label>
          <input type="date" className="w-full mb-4 border p-2 rounded" />
          <label className="block mb-2 font-semibold text-gray-700">Number of Guests:</label>
          <input type="number" className="w-full mb-4 border p-2 rounded" />
          <button className="bg-blue-600 text-white py-2 px-4 w-full rounded hover:bg-blue-500">
            Confirm Booking
          </button>
        </form>
      </div>
    );
  }
  
