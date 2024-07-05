import { useEffect, useState } from 'react';
import { Navigation } from "../navigation";

export const GraphicPage = () => {

    const [plotUrl, setPlotUrl] = useState('');

    useEffect(() => {
        fetch('http://127.0.0.1:8000/plot')
            .then(response => response.blob())
            .then(blob => {
                const url = URL.createObjectURL(blob);
                setPlotUrl(url);
            })
            .catch(error => console.error('Error fetching plot:', error));
    }, []);


    return (
        <div>
            <Navigation />
            <div className="pt-4 flex justify-center">
                {plotUrl ? (
                    <img src={plotUrl} alt="Plot" />
                ) : (
                    <p>Loading plot...</p>
                )}
            </div>
        </div>
    );
}