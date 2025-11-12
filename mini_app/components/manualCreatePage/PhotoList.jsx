import {ButtonUploadPhotosContainer} from "@components/manualCreatePage/ButtonUploadPhotos.jsx";
import {useEffect, useState} from "react";
import Gallery from "@components/manualCreatePage/BaseGallery.jsx";
import {Button} from "@maxhub/max-ui";
import {downloadMedias} from "@api/mediaDownload.js";

export function PhotoListContainer() {
    const [photos, setPhotos] = useState([]);

    useEffect(() => {
        return () => {
            photos.forEach(photo => {
                if (photo.objectURL) {
                    URL.revokeObjectURL(photo.objectURL);
                }
            });
        };
    }, []);

    const deletePhoto = (id) => {
        setPhotos(prevPhotos => {
            const photoToDelete = prevPhotos.find(photo => photo.id === id);
            if (photoToDelete?.objectURL) {
                URL.revokeObjectURL(photoToDelete.objectURL);
            }
            return prevPhotos.filter(photo => photo.id !== id);
        });
    }

    const addPhotos = (newFiles) => {
        setPhotos(prevPhotos => {
            const newPhotos = newFiles.map(file => ({
                id: Date.now() + Math.random(),
                file: file,
                objectURL: URL.createObjectURL(file)
            }));
            return [...prevPhotos, ...newPhotos];
        });
    }

    if (photos.length === 0) {
        return (
            <ButtonUploadPhotosContainer setPhotos={addPhotos}/>
        );
    } else {
        return (
            <PhotoListView
                deletePhoto={deletePhoto}
                images={photos}
                setPhotos={addPhotos}
            />
        );
    }
}

export function PhotoListView({images, setPhotos, deletePhoto}) {

    const sendPhoto = async () => {
        //TODO:Допилить отправку фото
        // let data = {
        //     images_base64: images.map((image) => image.file),
        //     user_id: urlParams.get("user_id"),
        //     latitude: coords.status === true ? String(coords.data.latitude) : '',
        //     longitude: coords.status === true ? String(coords.data.longitude) : '',
        //     filenames: []
        // }

        try {
            await downloadMedias();
        } catch (error) {
            console.error(error);
        }
    }

    return (
        images.length > 0 ? (
            <>
                <Gallery
                    images={images.map(photo => ({
                        src: photo.objectURL,
                        id: photo.id,
                        originalFile: photo.file
                    }))}
                    setPhotos={setPhotos}
                    deletePhoto={deletePhoto}
                />
                <Button
                    style={{
                        position: 'fixed',
                        bottom: '20px',
                        right: '20px',
                        zIndex: 2
                    }}
                    disabled={images.length === 10}
                    onClick={async () => {
                        await sendPhoto()
                    }
                    }
                >
                    Анализировать
                </Button>
            </>
        ) : (
            <div>Нет изображений</div>
        )
    );
}