import { Button } from "@maxhub/max-ui";
import { useState } from 'react';
import {ScannerModal} from "@components/createPage/ScannerButton.jsx";

export function WhatIsScanner() {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const openModal = () => setIsModalOpen(!isModalOpen);

    return (
        <>
            <Button mode="link" onClick={openModal}>
                Что такое сканер?
            </Button>

            <ScannerModal isOpen={isModalOpen} onClose={openModal} />
        </>
    );
}

