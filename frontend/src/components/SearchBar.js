import React, { useState, useEffect } from 'react';
import { OrangeWarningTrianlge, RedWarningTrianlge } from './warningTriangles';

export default function SearchBar({ recommendations = [] }) {
    const [query, setQuery] = useState('');
    const [spinner, setSpinner] = useState(false);
    const [error, setError] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [pongoSocket, setPongoSocket] = useState(null);
    const [socketHasClosed, setSocketHasClosed] = useState(false);
    const [listings, setListings] = useState([])
    const [searchParams, setSearchParams] = useState({})
    const [noData, setNoData] = useState(false)
    const [thinkingString, setThinkingString] = useState('')
    const [showPriceWarning, setShowPriceWarning] = useState(false)

    console.log(showPriceWarning)
    const SOCKET_URL = 'ws://localhost:8000/sockets/airbnb';
    // const SOCKET_URL = 'wss://smpl-backend.joinpongo.com/sockets/airbnb';


    useEffect(() => {
        const newPSocket = new WebSocket(SOCKET_URL);

        newPSocket.onopen = () => setSocketHasClosed(false);
        setPongoSocket(newPSocket);

        newPSocket.onmessage = (event) => {
            if (event.data.startsWith("PONGO_RESPONSE:")) {
                const data = JSON.parse(event.data.substring("PONGO_RESPONSE:".length));
                setListings(data);
            } else if (event.data.startsWith("COMPLETION_RESPONSE:")) {

                    const data = JSON.parse(event.data.substring("COMPLETION_RESPONSE:".length));
                    setSearchParams(data);
                    setThinkingString('done')


            } else if (event.data.startsWith("NO_DATA_FOUND")) {
                setNoData(true);
                setListings([])
            }
        };

        newPSocket.onclose = () => {
            setSocketHasClosed(true);
        };
    }, []);



    async function search(event, inputQuery = query) {
        if (event !== 'no-event') {
            event.preventDefault();
        }
        setSpinner(true);
        setError(false);
        setErrorMessage("");
        setThinkingString('Thinking...')
        setNoData(false)
        pongoSocket.send(inputQuery);
        setSpinner(false);
    }

    const handleChange = (e) => {
        const price_terms = ['price', 'cost', '$', 'usd', 'dollars', 'per night', 'under']
        const containsPriceTerm = price_terms.some(term => e.target.value.toLowerCase().includes(term.toLowerCase()));
        if (containsPriceTerm) {
            setShowPriceWarning(true);
        } else {
            setShowPriceWarning(false)
        }
        setQuery(e.target.value);
    };

    const makeThinkingString = () => {
    let output = 'Searching for listings with:\n'

    for (const [key, value] of Object.entries(searchParams)) {
        if (typeof value !== 'object') {
            continue;
        }

        let keyString = key;
        switch (key) {
            case 'allows_pets':
                keyString = 'Allows pets';
                break;
            case '8':
                keyString = 'Has a kitchen';
                break;
            case '1':
                keyString = 'Has a TV';
                break;
            case '4':
                keyString = 'Has Wifi';
                break;
            case '5':
                keyString = 'Has Air Conditioning';
                break;
            case '9':
                keyString = 'Has free parking';
                break;
            case '30':
                keyString = 'Has heating';
                break;
            case '33':
                keyString = 'Has a washer';
                break;
            case '34':
                keyString = 'Has a dryer';
                break;
            case '101':
                keyString = 'Has a back yard';
                break;
            case 'address':
                keyString = 'Location';
                break;
            case 'bathroom_label':
                keyString = 'Bathrooms';
                break;
            case 'allows_smoking':
                keyString = 'Smoking allowed';
                break;
            case 'bedroom_count':
                keyString = 'Bedrooms';
                break;
            case 'bed_count':
                keyString = 'Beds';
                break;
            default:
                break;
        }
        output += `${keyString} ${value['operator']} ${value['valueNumber'] || value['valueBoolean'] || value['valueString']} \n`;
    }
    output = output.replace(/Equal/g, '=').replace(/GreaterThan/g, '>').replace(/LessThan/g, '<');

    if(output === 'Searching for listings with:\n') {
        return ''
    } else return output;
    }

    return (
        <div className='md:w-full mx-auto pb-10 w-[95vw]'>
            <div className='w-full flex flex-col'>
                <div className='flex w-full sm:px-10 py-2 mx-auto flex-col'>
                    <div className='flex'>
                        {socketHasClosed ? (
                            <div className='text-red-500 flex items-center w-fit h-fit mb-1 mt-auto'>
                                <div className='w-4 h-4 mr-1 mt-0.5'>
                                    <RedWarningTrianlge />
                                </div>
                                <div className='flex sm:text-md text-sm items-center text-right'>
                                    Connection to server lost, please refresh the page
                                </div>
                            </div>
                        ) : showPriceWarning ? <div className='text-orange-500 flex items-center w-fit h-fit mb-1 mt-auto'>
                        <div className='w-4 h-4 mr-1 mt-0.5'>
                            <OrangeWarningTrianlge />
                        </div>
                        <div className='flex sm:text-md text-sm items-center text-right'>
                            Queries on price are not supported
                        </div>
                    </div>: null}
                    </div>
                    <div className="flex items-center align-middle">
                        <form className='w-full flex'>
                            <input
                                className="h-11 flex items-center border-none outline-none focus: w-full text-white mr-3 py-3 px-4 bg-zinc-700 shadow-md rounded-none leading-tight focus:ring-2 focus:ring-indigo-600 focus:outline-none"
                                type="text"
                                value={query}
                                id='search-bar-'
                                onChange={handleChange}
                                placeholder="Search..."
                            />
                            <button
                                className="bg-indigo-600 text-white px-4 py-2 rounded-none"
                                type="submit"
                                onClick={search}
                            >
                                Search
                            </button>
                        </form>
                    </div>
                    {recommendations.length > 0 && <div className='w-full flex justify-evenly items-stretch sm:flex-row mt-4 md:mt-4'>
                {recommendations.map((item, idx) => {
                    return <div key={idx} className='cursor-pointer w-fit rounded-none py-1.5 md:py-2 px-2 md:px-3 shadow-md text-white bg-zinc-600 text-medium mx-3 sm:mt-0 text-xs md:text-base' onClick={()=>{setQuery(item);}}>
                        {item}
                    </div>
                })}
                

                </div>}
                    {spinner && <div className="spinner">Loading...</div>}
                    {error && <div className="error">{errorMessage}</div>}
                    {noData && <div className='text-lg w-fit mx-auto mt-20 text-2xl font-semibold'>Couldn't find any listings for that query, please try another</div>}
                    {thinkingString !== '' && <div className='mt-5 font-medium font-mono whitespace-pre-wrap mx-auto text-center'>{thinkingString !== 'Thinking...' ? makeThinkingString(searchParams) : thinkingString}</div>}
                    <div className="flex flex-wrap justify-center gap-x-20 gap-y-20 w-full mx-auto mt-10">
                        {listings.map((item, idx) => {
                            console.log(item)
                    return <a href={item['url']} className='w-fit h-fit bg-zinc-700 rounded shadow-xl' target='_blank' key={idx} rel="noreferrer">
                                <img src={item['thumbnail']} alt={item['name']} className='w-full max-w-[30rem] rounded-top'/>

                            <div  className='w-full max-w-[30rem] h-fit flex flex-col px-3 pt-1 pb-3'>
                            {/* <div className='w-full max-h-32'> */}

                            <div className='text-3xl font-semibold mt-1'>{item['name']}</div>
                            <div className='text-lg mt-1 font-medium'>{item['address']}</div>
                            
                            <div className='mt-1'>

                                {
                                    (item['text'].includes("Review:") 
                                        ? item['text'].substring(item['text'].indexOf("Review:")).substring(0, 100) + '...'
                                        : item['text'].substring(item['text'].indexOf("Description:")).substring(0, 100) + '...')
                                    .replace(/<\/?[^>]+(>|$)|&nbsp;/g, "")
                                }
                            </div>
                            </div>
                        </a>
                })}</div>
                </div>
            </div>
        </div>
    );
}
                               