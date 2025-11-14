import {Typography} from "@maxhub/max-ui";

export function StepNumber({step}) {
    return (
        <>
            <div
                style={{
                    backgroundColor: '#E2F0FF',
                    height: 40,
                    width: 40,
                    borderRadius: '10px',
                    color: '#0081ff',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                }}
            >
                <Typography.Action>
                    {step}
                </Typography.Action>
            </div>
        </>
    )
}