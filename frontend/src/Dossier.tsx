import styles from './style/Dossier.module.scss';
import React from 'react';
import Image from './assets/adams.png'

export default function Dossier() {
    return (<div><div className={styles.card}>
        <div className={styles.title}>ADRIENNE ADAMS</div>
        <img className={styles.image} src={Image} />
        <div className={styles.districtOverlay}>
            <div className={styles.districtHeading}>
                District 28
            </div>
            <div className={styles.districtSubheading}>
                Queens
            </div>
            <div className={styles.districtNeighborhoods}>
                Jamaica, Richmond Hill, Rochdale Village, South Ozone Park
            </div>
        </div>
        <div className={styles.party}>
                Democrat
            </div>
    </div>
    <div className={styles.backCard}>
        <div className={styles.infoSection}>
            <div className={styles.infoHeading}>
                COUNCILMEMBER INFO
            </div>
            <div className={styles.infoBody}>
                <div><strong>Name:</strong> Adrienne Adams, Speaker</div>
                <div><strong>Committees:</strong> [enter them here]</div>
                <div><strong>Caucuses:</strong> [enter them here]</div>
            </div>
        </div>
        <div>
            <div className={styles.bioHeading}>
                BIO
            </div>
            <div className={styles.bioBody}>
            <p>Before helming Community Board 12 and being elected CM was a former Corporate Trainer who worked in Human Capital Management at several Fortune 500 corporations, specializing in Executive Training and Telecom Management. Served as a Child Development Associate Instructor, training child care professionals.</p>
<p><b>Priorities:</b> Seeing the city through the pandemic and working to strengthen families that have been damaged in its wake.</p>
<p><b>Other Notes:</b> Strong education focus. Attended same high school as Mayor Adams. An AKA. Attended Spelman as did CM Hudson.</p>
<p><b>Schooling/Achievements:</b> [enter here]</p>
            </div>
            <div className={styles.quote}>
            “All roads lead through this pandemic,” she said. “When I think of my priorities, I think of rebuilding a city.” 
            </div>
        </div>
    </div>
    </div>
    );
}