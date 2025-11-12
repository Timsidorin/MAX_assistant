import { Flex } from "@maxhub/max-ui";
import { useState, useEffect } from "react";
import styles from "@assets/styles/module/BaseGallery.module.css";
import {useFileDialog} from "@hooks/useFileDialog";
import { FiTrash } from "react-icons/fi";

export default function BaseGallery({ images, setPhotos, deletePhoto }) {
    const [selectedImageId, setSelectedImageId] = useState(null);

    const fileDialog = useFileDialog({
        accept: 'image/*',
        maxFiles: images.length === 10 ? 0 : 10 - images.length,
        multiple: true
    });

    useEffect(() => {
        if (fileDialog.files && fileDialog.files.length > 0) {
            setPhotos(fileDialog.files);
            fileDialog.reset();
        }
    }, [fileDialog.files, setPhotos, fileDialog]);

    const addPhotos = () => {
        fileDialog.open();
    }

    const handleImageClick = (image) => {
        setSelectedImageId(image.id);
    };

    const closeLightbox = () => {
        setSelectedImageId(null);
    };

    const goToNext = () => {
        if (selectedImageId) {
            const currentIndex = images.findIndex(img => img.id === selectedImageId);
            const nextIndex = (currentIndex + 1) % images.length;
            setSelectedImageId(images[nextIndex]?.id || null);
        }
    };

    const goToPrev = () => {
        if (selectedImageId) {
            const currentIndex = images.findIndex(img => img.id === selectedImageId);
            const prevIndex = (currentIndex - 1 + images.length) % images.length;
            setSelectedImageId(images[prevIndex]?.id || null);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowRight') goToNext();
        if (e.key === 'ArrowLeft') goToPrev();
    };

    const handleDelete = () => {
        if (selectedImageId) {
            deletePhoto(selectedImageId);
            closeLightbox();
        }
    }

    const selectedImage = selectedImageId
        ? images.find(img => img.id === selectedImageId)
        : null;

    const currentIndex = selectedImageId
        ? images.findIndex(img => img.id === selectedImageId) + 1
        : 0;

    useEffect(() => {
        const galleryContainer = document.querySelector(`.${styles.galleryScrollContainer}`);
        if (galleryContainer) {
            galleryContainer.style.paddingBottom = '80px';
        }
    }, []);

    return (
        <>
            <div className={styles.galleryScrollContainer}>
                <Flex gap={16} wrap="wrap" justify="center" className={styles.galleryContainer}>
                    {/* Кнопка добавления новой фотографии */}
                    {images.length === 10 ? '' : <div
                        className={styles.addImageItem}
                        onClick={addPhotos}
                    >
                        <div className={styles.addImageIcon}>+</div>
                        <span className={styles.addImageText}>Добавить фото</span>
                    </div>}

                    {/* Существующие фотографии */}
                    {images.map((image) => (
                        <div
                            key={image.id}
                            className={styles.galleryItem}
                            onClick={() => handleImageClick(image)}
                        >
                            <img
                                src={image.src}
                                alt={image.alt || 'Изображение галереи'}
                                className={styles.galleryImage}
                                loading="lazy"
                            />
                            {image.title && (
                                <div className={styles.imageOverlay}>
                                    <span className={styles.imageTitle}>{image.title}</span>
                                </div>
                            )}
                        </div>
                    ))}
                </Flex>
            </div>

            {selectedImage && (
                <div
                    className={styles.lightbox}
                    onClick={closeLightbox}
                    onKeyDown={handleKeyDown}
                    tabIndex={0}
                    autoFocus
                >
                    <div className={styles.lightboxContent} onClick={(e) => e.stopPropagation()}>
                        <button className={styles.closeButton} onClick={closeLightbox}>
                            ×
                        </button>

                        <button className={styles.navButton} onClick={goToPrev} style={{ left: '20px' }}>
                            ‹
                        </button>

                        <div className={styles.lightboxImageContainer}>
                            <img
                                src={selectedImage.src}
                                alt={selectedImage.alt || 'Изображение галереи'}
                                className={styles.lightboxImage}
                            />
                            {(selectedImage.title || selectedImage.description) && (
                                <div className={styles.imageInfo}>
                                    {selectedImage.title && <h3>{selectedImage.title}</h3>}
                                    {selectedImage.description && <p>{selectedImage.description}</p>}
                                </div>
                            )}
                        </div>

                        <button className={styles.navButton} onClick={goToNext} style={{ right: '20px' }}>
                            ›
                        </button>

                        {/* Кнопка удаления */}
                        <button
                            className={styles.deleteButton}
                            onClick={handleDelete}
                            title="Удалить фото"
                        >
                            <FiTrash size={20} />
                        </button>

                        <div className={styles.imageCounter}>
                            {currentIndex} / {images.length}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}