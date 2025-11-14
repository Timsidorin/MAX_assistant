import {ButtonUploadPhotosContainer} from "@components/manualCreatePage/ButtonUploadPhotos.jsx";
import {useEffect, useState} from "react";
import Gallery from "@components/manualCreatePage/BaseGallery.jsx";
import {Button} from "@maxhub/max-ui";
import {downloadMedias} from "@api/mediaDownload.js";
import {useParams, useNavigate} from 'react-router';
import {sendReport} from "@api/ticket.js";
import {BaseLoader} from "@components/ui/BaseLoader.jsx";

export function PhotoListContainer() {
    const [photos, setPhotos] = useState([]);
    const router = useParams();
    const navigate = useNavigate();
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
                router={router}
                navigate={navigate}
                deletePhoto={deletePhoto}
                images={photos}
                setPhotos={addPhotos}
            />
        );
    }
}

export function PhotoListView({images, setPhotos, deletePhoto, router, navigate}) {
    const [loading, setLoading] = useState(false);

    const fileToBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = error => reject(error);
        });
    };

    const sendPhoto = async () => {
        try {
            const imagesBase64 = await Promise.all(
                images.map(async (photo) => {
                    return await fileToBase64(photo.file);
                })
            );

            const filenames = images.map(photo => photo.file.name || `image_${photo.id}.jpg`);

            let data = {
                images_base64: imagesBase64,
                user_id: String(window.WebApp.initDataUnsafe.user.id),
                latitude: router.lat ?? '',
                longitude: router.long ?? '',
                filenames: filenames
            }

            let response = await downloadMedias(data);

            let total_potholes = {
                average_risk: 0,
                max_risk: 0,
                detections: {
                    CRITICAL: 0,
                    HIGH: 0,
                    MEDIUM: 0,
                    LOW: 0,
                    total_potholes: 0
                }
            };
            let imageUrls = [];
            response.data.results.forEach((element) => {
                imageUrls.push(element.image_url);
                total_potholes.average_risk = element.average_risk > total_potholes.average_risk
                    ? element.average_risk : total_potholes.average_risk;
                total_potholes.max_risk = element.max_risk > total_potholes.max_risk
                    ? element.max_risk : total_potholes.max_risk;
                total_potholes.detections.CRITICAL += element.detections.CRITICAL;
                total_potholes.detections.HIGH += element.detections.HIGH;
                total_potholes.detections.MEDIUM += element.detections.MEDIUM;
                total_potholes.detections.LOW += element.detections.LOW;
                total_potholes.detections.total_potholes += element.total_potholes;
            });
            let body = {
                user_id: response.data.user_id,
                latitude: response.data.latitude,
                longitude: response.data.longitude,
                address: response.data.address,
                image_urls: imageUrls,
                total_potholes: total_potholes.detections.total_potholes,
                ...total_potholes,
            };

            let uuid = await sendReport(body);
            navigate(`/send-report/${uuid.data.uuid}`)
        } catch (error) {
            console.error('Ошибка при отправке фото:', error);
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
                    disabled={images.length === 10 || loading}
                    onClick={async () => {
                        setLoading(true);
                        try {
                            await sendPhoto();
                        } finally {
                            setLoading(false);
                        }
                    }
                    }
                >
                    {loading ? <BaseLoader style={{width: '100px'}} /> : 'Анализировать'}
                </Button>
                {loading && (
                    <div style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        background: 'rgba(255, 255, 255, 0.8)',
                        backdropFilter: 'blur(5px)',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        zIndex: 1000
                    }}>
                        <BaseLoader />
                    </div>
                )}
            </>
        ) : (
            <div>Нет изображений</div>
        )
    );
}