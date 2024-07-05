import { Link } from "react-router-dom";

export const Navigation = () => {
    return (
        <nav className="flex justify-center border-b border-gray-200 w-full py-4">
            <ul className="flex flex-row gap-20">
                <li><Link to="/form" >Form</Link></li>
                <li><Link to="/graphic">Gráfico</Link></li>
            </ul>
        </nav>
    );
};
