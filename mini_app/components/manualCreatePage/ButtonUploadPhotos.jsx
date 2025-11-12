import styles from '@assets/styles/module/ButtonUploadPhotos.module.css';
import {useEffect} from "react";
import {useFileDialog} from "@hooks/useFileDialog";

export function ButtonUploadPhotosContainer(props) {
    const fileDialog = useFileDialog({
        accept: 'image/*',
        maxFiles: 10,
        multiple: true
    });

    useEffect(() => {
        if (fileDialog.files) {
            props.setPhotos(fileDialog.files);
        }
        if (fileDialog.error) {
            console.log(fileDialog.error);
        }
    }, [fileDialog.files]);

    return (
        <>
            <ButtonUploadPhotosViews onAction={fileDialog.open}/>
        </>
    )
}

function ButtonUploadPhotosViews(props) {
    return (
        <>
            <div onClick={() => props.onAction()} className={styles['input-div']}>
                <svg xmlns="http://www.w3.org/2000/svg" width="2em" height="1.5em"
                     viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     className={styles['icon']}>
                    <polyline points="16 16 12 12 8 16"></polyline>
                    <line y2="21" x2="12" y1="12" x1="12"></line>
                    <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"></path>
                    <polyline points="16 16 12 12 8 16"></polyline>
                </svg>
            </div>
        </>
    )
}