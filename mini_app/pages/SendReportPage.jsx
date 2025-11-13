import { useParams } from "react-router";
import {ListStepsContainer} from "@components/sendReportPage/ListSteps.jsx";

export function SendReportPage() {
    let params = useParams();
    return (
        <>
            <ListStepsContainer />
        </>
    );
}