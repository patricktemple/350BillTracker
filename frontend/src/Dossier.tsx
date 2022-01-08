import styles from './style/Dossier.module.scss';
import React from 'react';

export interface DossierPerson {
    name: string;
    district: number;
    borough: string;
    neighborhoods: string;
    party: string;
    title: string;

    twitter: string;
    // followers: number;

    bio: string;

    priorities: string;
    otherNotes: string;

    quote: string;
    email: string;
    image: any;
}

interface Props {
    dossierPerson: DossierPerson;
}

export default function Dossier(props: Props) {
    const person = props.dossierPerson;

    return (<div><div className={styles.card}>
        <div className={styles.title}>{person.name}</div>
        <img className={styles.image} src={person.image} />
        <div className={styles.districtOverlay}>
            <div className={styles.districtHeading}>
                District {person.district}
            </div>
            <div className={styles.districtSubheading}>
                {person.borough}
            </div>
            <div className={styles.districtNeighborhoods}>
                {person.neighborhoods}
            </div>
        </div>
        <div className={styles.party}>
                {person.party}
            </div>
    </div>
    <div className={styles.backCard}>
        <div className={styles.infoSection}>
            <div className={styles.infoHeading}>
                COUNCILMEMBER INFO
            </div>
            <div className={styles.infoBody}>
                <div><strong>Name:</strong> {person.name}, {person.title}</div>
                <div><strong>Committees:</strong> [enter them here]</div>
                <div><strong>Caucuses:</strong> [enter them here]</div>
            </div>
        </div>
        <div>
            <div className={styles.socialMediaSection}>
                <div className={styles.socialMediaLeft}><div><b>Twitter:</b> @{person.twitter}</div>
                <div><b>Followers:</b> 2500</div></div>
                <div className={styles.socialMediaRight}>
                    <div>
                        <b>Campaign funds:</b> $1000
                    </div>
                    <div>
                        <b>Contributions:</b> $1000
                    </div>
                </div>
            </div>
            <div className={styles.bioHeading}>
                BIO
            </div>
            <div className={styles.bioBody}>
            <p>{person.bio}</p>
<p><b>Priorities:</b> {person.priorities}</p>
<p><b>Other Notes:</b> {person.otherNotes}</p>
<p><b>Schooling/Achievements:</b> [enter here]</p>
            </div>
            <div className={styles.quote}>
            {person.quote}
            </div>
            <div className={styles.email}>
                {person.email}
            </div>
        </div>
    </div>
    </div>
    );
}