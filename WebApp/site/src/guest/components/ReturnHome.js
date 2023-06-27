import React from 'react';
import { Link } from 'react-router-dom';
import './ReturnHome.css';

export default function ReturnHome() {
    return (
        <div id="return-home">
            <Link to="/">Home</Link>
        </div>
    );
}
