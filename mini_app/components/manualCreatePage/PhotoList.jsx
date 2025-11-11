import {ButtonUploadPhotosContainer} from "@components/manualCreatePage/ButtonUploadPhotos.jsx";
import {useState} from "react";

export function PhotoListContainer() {
    const [photos, setPhotos] = useState([]);

    if (photos.length === 0) {
        return (
            <>
                <ButtonUploadPhotosContainer setPhotos={setPhotos} />
            </>
        );
    } else {
        return (
          <PhotoListView />
        );
    }
}

export function PhotoListView() {
    return (
        <div>

        </div>
    );

}