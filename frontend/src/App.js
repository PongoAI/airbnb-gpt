import React from 'react';
import SearchBar from './components/SearchBar';

// const SOCKET_URL = 'wss://smpl-backend.joinpongo.com/sockets/test'




export default function App() {



  return (
    <div className="min-h-screen h-fit w-screen bg-zinc-900 flex flex-col text-white">
      <div className="flex pt-5 md:pt-3 px-5">
        <div className="mt-auto text-sm"><a href='https://github.com/PongoAI/airbnb-gpt' className="underline">View source code</a></div>
        <div className="ml-auto ">An experiment by <a href='https://joinpongo.com?utm_source=airbnbgpt' className="underline">Pongo 🦧</a></div>
      </div>

      <div className='w-fit mx-auto pt-10 mb-2 text-4xl font-semibold'>AirbnbGPT</div>
      <div className='w-fit mx-auto text-zinc-400 text-center max-w-[90vw] text-md mb-3'>Semantic search demo through Airbnb listing reviews and descriptions. <br></br>Also filters by # bedrooms, # bathrooms, has stocked kitchen, washer/dryer, A/C, heaitng, etc.</div>
      <SearchBar recommendations={["Show me cozy listings with A/C, TV, and Wifi in San Francisco", "Futuristic listings with free parking and at least 3 beds", "Pet-friendly listings with a back yard"]} skipCohere={true}/>




    </div>
  );
}
